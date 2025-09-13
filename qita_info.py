import re
import search_model


async def main(qita):
    qita_name, wikitext = await search_model.get_operator_wikitext(qita)

    if not wikitext:
        return None

    # 直接正则找出各项
    miao_shu = re.search(r"\|描述\s*=\s*(.+)", wikitext)
    yong_tu = re.search(r"\|用途\s*=\s*(.+)", wikitext)
    huode_fangshi = re.search(r"\|获得方式\s*=\s*(.+)", wikitext)
    fen_lei = re.search(r"\|分类\s*=\s*(.+)", wikitext)

    # 没找到就返回“未找到…”
    # 注意：这里也简单处理了下strip()，防止解析出多余的空格
    miao_shu = miao_shu.group(1).strip() if miao_shu else "未找到描述"
    yong_tu = yong_tu.group(1).strip() if yong_tu else "未找到用途"
    huode_fangshi = huode_fangshi.group(1).strip() if huode_fangshi else "未找到获得方式"
    fen_lei = fen_lei.group(1).strip() if fen_lei else "未找到分类"

    return qita_name, miao_shu, yong_tu, huode_fangshi, fen_lei