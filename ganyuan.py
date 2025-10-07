import re, logging
from collections import namedtuple
from search_model import search_model

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OperatorInfo = namedtuple('OperatorInfo',
                          ['name', 'zhi_ye', 'fen_zhi', 'xing_ji', 'te_xing', 'te_xing_b', 'wikitext'])
""" 待完善
"name": "干员名称",
"zhi_ye": "职业",
"fen_zhi": "分支",
"xing_ji": "稀有度",
"te_xing": "特性",
"te_xing_b": "特性备注",
"wikitext": "wikitext"
"""

# 预编译正则表达式以提高性能
COLOR_PATTERN = re.compile(r'\{\{color\|#[0-9A-F]{6}\|(.*?)}}')
LINK_PATTERN_1 = re.compile(r'\[\[([^]|]+)\|([^]]+)]]')
LINK_PATTERN_2 = re.compile(r'\[\[([^]]+)]]')
BOLD_ITALIC_PATTERN = re.compile(r"''+(.*?)''+")


class Ganyuan:
    def __init__(self, config=None):
        self.config = config
        self.image_output = self.config["image"]["ganyuan_image_output"]

        # 预编译字段正则表达式
        self.field_patterns = {
            'zhi_ye': re.compile(r"\|职业\s*=\s*(.+)"),
            'fen_zhi': re.compile(r"\|分支\s*=\s*(.+)"),
            'xing_ji': re.compile(r"\|稀有度\s*=\s*(.+)"),
            'te_xing': re.compile(r"\|特性\s*=\s*(.+)"),
            'te_xing_b': re.compile(r"\|特性备注\s*=\s*\s*(.+)"),
        }

    def clean_wikitext(self, text):
        """清理wikitext中的标记，提取纯文本内容（同步版本）"""
        if not text:
            return ""  # 返回空字符串而不是None

        # 移除颜色标记 {{color|#00B0FF|回旋投射物}}
        text = COLOR_PATTERN.sub(r'\1', text)

        # 移除其他常见的wikitext标记
        text = LINK_PATTERN_1.sub(r'\2', text)  # [[链接|显示文字]] -> 显示文字
        text = LINK_PATTERN_2.sub(r'\1', text)  # [[链接]] -> 链接
        text = BOLD_ITALIC_PATTERN.sub(r'\1', text)  # 移除粗体和斜体标记
        text = text.replace('*', '')
        return text.strip()

    async def get_operator_image(self, name: str, skin):
        """异步获取干员的image，默认为精二皮"""
        name = re.sub(r'[（）]', lambda m: {'（': '(', '）': ')'}.get(m.group(0)), name)
        if "时装" or "皮肤" in skin:
            skin = re.sub("时装|皮肤", "skin", skin)
        name = f"文件:立绘 {name} {skin}.png"
        return await search_model.get_images_url([name])

    async def get_operator_info_concurrently(self, name: str, skin="2"):
        """并发获取干员信息和图片，提高处理速度"""
        try:
            name = await search_model.search_wikitext(name)
            name_out, wikitext = await search_model.get_wikitext(name)
            if self.image_output:
                image_url = await self.get_operator_image(name, skin)
            else:
                image_url = ""
            return name_out, wikitext, image_url
        except (search_model.httpx.HTTPStatusError, search_model.httpx.RequestError) as e:
            logger.error(f"获取干员信息失败: {e}")
            return name, None, []
        except Exception as e:
            logger.error(f"获取干员信息时发生未知错误: {e}")
            return name, None, []

    async def clean_over_wiki(self, ganyuan, skin):
        # 并发获取干员信息和图片，提高处理速度
        name, wikitext, image = await self.get_operator_info_concurrently(ganyuan, skin)

        if not wikitext:
            return None, None

        # 批量处理正则表达式查找和结果处理
        results = {}

        for field_name, pattern in self.field_patterns.items():
            match = pattern.search(wikitext)
            if match:
                raw_value = match.group(1)
                if field_name in ['zhi_ye', 'fen_zhi', 'te_xing', 'te_xing_b']:
                    # 直接同步处理wikitext清理，避免异步开销
                    results[field_name] = self.clean_wikitext(raw_value)
                elif field_name == 'xing_ji':
                    # 处理稀有度
                    results[field_name] = str(f"{int(raw_value.strip()) + 1}星")
                else:
                    results[field_name] = raw_value
            else:
                results[field_name] = None

        # 返回图片和操作员信息
        return image, OperatorInfo(name, results['zhi_ye'], results['fen_zhi'],
                                   results['xing_ji'], results['te_xing'], results['te_xing_b'], wikitext)

    async def run(self, ganyuan=None):
        if ganyuan is None:
            ganyuan = input("请输入干员名称：")
        # ganyuan = "娜仁图亚"
        """
        result含有的参数（按顺序）：
        name, zhi_ye, fen_zhi, xing_ji, te_xing, te_xing_b, wikitext
        """
        parts = re.split(r'[\s,，]+', ganyuan)
        parts = [part.strip() for part in parts if part.strip()]
        # 处理输入参数不足的情况，提供默认值
        ganyuan_name = parts[0] if len(parts) > 0 else ""
        skin = parts[1] if len(parts) > 1 else "2"
        image, result = await self.clean_over_wiki(ganyuan_name, skin)
        if result:
            # print(wikitext)
            if self.image_output:
                print(image)
            else:
                print(f"是否输出图片：{self.image_output}")
            print(f"干员：{result.name}")
            print(f"职业：{result.zhi_ye}")
            print(f"分支：{result.fen_zhi}")
            print(f"稀有度：{result.xing_ji}")
            print(f"特性：{result.te_xing}")
            if result.te_xing_b is not None:
                print(f"特性备注：{result.te_xing_b}")
            return image, result
        else:
            print("未找到该干员的信息。")
            return None, None

# 延迟初始化
ganyuan_instance = None

def initialize_ganyuan(config):
    global ganyuan_instance
    if ganyuan_instance is None:
        ganyuan_instance = Ganyuan(config)
    return ganyuan_instance
