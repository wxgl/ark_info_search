import re
import search_model
from collections import namedtuple

OperatorInfo = namedtuple('OperatorInfo',
                          ['name', 'zhi_ye', 'fen_zhi', 'xing_ji', 'te_xing', 'te_xing_b', 'wikitext'])


def clean_wikitext(text):
    """清理wikitext中的标记，提取纯文本内容"""
    if not text:
        return ""  # 返回空字符串而不是None

    # 移除颜色标记 {{color|#00B0FF|回旋投射物}}
    text = re.sub(r'\{\{color\|#[0-9A-F]{6}\|(.*?)}}', r'\1', text)

    # 移除其他常见的wikitext标记
    text = re.sub(r'\[\[([^]|]+)\|([^]]+)]]', r'\2', text)  # [[链接|显示文字]] -> 显示文字
    text = re.sub(r'\[\[([^]]+)]]', r'\1', text)  # [[链接]] -> 链接
    text = re.sub(r"''+(.*?)''+", r'\1', text)  # 移除粗体和斜体标记
    text = text.replace('*', '')
    return text.strip()


async def main(ganyuan):
    name, wikitext = await search_model.get_operator_wikitext(ganyuan)

    if not wikitext:
        return None

    # 定义要查找的字段及对应的正则表达式和处理方式
    fields = [
        ('zhi_ye', r"\|职业\s*=\s*(.+)", lambda x: clean_wikitext(x)),
        ('fen_zhi', r"\|分支\s*=\s*(.+)", lambda x: clean_wikitext(x)),
        ('xing_ji', r"\|稀有度\s*=\s*(.+)", lambda x: str(f"{int(x.strip()) + 1}星")),
        ('te_xing', r"\|特性\s*=\s*(.+)", lambda x: clean_wikitext(x)),
        ('te_xing_b', r"\|特性备注\s*=\s*\s*(.+)", lambda x: clean_wikitext(x))
    ]

    # 批量处理正则表达式查找和结果处理
    results = {}
    for field_name, pattern, process_func in fields:
        match = re.search(pattern, wikitext)
        if match:
            results[field_name] = process_func(match.group(1))
        else:
            results[field_name] = None
    return OperatorInfo(name, results['zhi_ye'], results['fen_zhi'], results['xing_ji'],
                        results['te_xing'], results['te_xing_b'], wikitext)


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(main("娜仁图亚"))
    print(f"干员：{result.name}")
    print(f"职业：{result.zhi_ye}")
    print(f"分支：{result.fen_zhi}")
    print(f"稀有度：{result.xing_ji}")
    print(f"特性：{result.te_xing}")
    print(f"特性备注：{result.te_xing_b}")
