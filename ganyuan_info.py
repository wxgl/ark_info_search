import re
import search_model

def main(ganyuan):
    name, wikitext = search_model.get_operator_wikitext(ganyuan)
    # 直接正则找出各项
    zhi_ye = re.search(r"\|职业\s*=\s*(.+)", wikitext)
    fen_zhi = re.search(r"\|分支\s*=\s*(.+)", wikitext)
    xing_ji = re.search(r"\|稀有度\s*=\s*(.+)", wikitext)

    # 没找到就返回“未找到…”
    zhi_ye = zhi_ye.group(1).strip() if zhi_ye else "未找到职业"
    fen_zhi = fen_zhi.group(1).strip() if fen_zhi else "未找到分支"
    xing_ji = str(f"{int(xing_ji.group(1).strip()) + 1}星") if xing_ji else "未找到稀有度"

    return name, zhi_ye, fen_zhi, xing_ji
