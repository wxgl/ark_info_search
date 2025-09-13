import re
import search_model


def clean_wikitext(text):
    """清理wikitext中的标记，提取纯文本内容"""
    if not text:
        return "" # 返回空字符串而不是None

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

    # 直接正则找出各项
    zhi_ye = re.search(r"\|职业\s*=\s*(.+)", wikitext)
    fen_zhi = re.search(r"\|分支\s*=\s*(.+)", wikitext)
    xing_ji = re.search(r"\|稀有度\s*=\s*(.+)", wikitext)
    te_xing = re.search(r"\|特性\s*=\s*(.+)", wikitext)
    te_xing_b = re.search(r"\|特性备注\s*=\s*\s*(.+)", wikitext)

    # 没找到就返回“未找到…”
    zhi_ye = clean_wikitext(zhi_ye.group(1)) if zhi_ye else "未找到职业"
    fen_zhi = clean_wikitext(fen_zhi.group(1)) if fen_zhi else "未找到分支"
    xing_ji = str(f"{int(xing_ji.group(1).strip()) + 1}星") if xing_ji else "未找到稀有度"
    te_xing = clean_wikitext(te_xing.group(1)) if te_xing else "未找到特性"
    te_xing_b = clean_wikitext(te_xing_b.group(1)) if te_xing_b else "未找到特性备注"

    return name, zhi_ye, fen_zhi, xing_ji, te_xing, te_xing_b