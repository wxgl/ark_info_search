import re
from . import search_model
from collections import namedtuple

OperatorInfo = namedtuple('OperatorInfo',
                          ['name', 'zhi_ye', 'fen_zhi', 'xing_ji', 'te_xing', 'te_xing_b', 'wikitext'])

# 预编译正则表达式以提高性能
COLOR_PATTERN = re.compile(r'\{\{color\|#[0-9A-F]{6}\|(.*?)}}')
LINK_PATTERN_1 = re.compile(r'\[\[([^]|]+)\|([^]]+)]]')
LINK_PATTERN_2 = re.compile(r'\[\[([^]]+)]]')
BOLD_ITALIC_PATTERN = re.compile(r"''+(.*?)''+")


def clean_wikitext(text):
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


# 预编译字段正则表达式
FIELD_PATTERNS = {
    'zhi_ye': re.compile(r"\|职业\s*=\s*(.+)"),
    'fen_zhi': re.compile(r"\|分支\s*=\s*(.+)"),
    'xing_ji': re.compile(r"\|稀有度\s*=\s*(.+)"),
    'te_xing': re.compile(r"\|特性\s*=\s*(.+)"),
    'te_xing_b': re.compile(r"\|特性备注\s*=\s*\s*(.+)"),
}


async def clean_over_wiki(ganyuan, skin):
    # 并发获取干员信息和图片，提高处理速度
    name, wikitext, image = await search_model.get_operator_info_concurrently(ganyuan, skin)

    if not wikitext:
        return None, None

    # 批量处理正则表达式查找和结果处理
    results = {}

    for field_name, pattern in FIELD_PATTERNS.items():
        match = pattern.search(wikitext)
        if match:
            raw_value = match.group(1)
            if field_name in ['zhi_ye', 'fen_zhi', 'te_xing', 'te_xing_b']:
                # 直接同步处理wikitext清理，避免异步开销
                results[field_name] = clean_wikitext(raw_value)
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


async def main(ganyuan=None, skin: str = "2"):
    if ganyuan is None:
        ganyuan = input("请输入干员名称：")
    # ganyuan = "娜仁图亚"
    """
    result含有的参数（按顺序）：
    name, zhi_ye, fen_zhi, xing_ji, te_xing, te_xing_b, wikitext
    """
    image, result = await clean_over_wiki(ganyuan, skin)
    if result:
        # print(wikitext)
        print(image)
        print(f"干员：{result.name}")
        print(f"职业：{result.zhi_ye}")
        print(f"分支：{result.fen_zhi}")
        print(f"稀有度：{result.xing_ji}")
        print(f"特性：{result.te_xing}")
        if result.te_xing_b is not None:
            print(f"特性备注：{result.te_xing_b}")
    else:
        print("未找到该干员的信息。")
    await search_model.close_http_client()
