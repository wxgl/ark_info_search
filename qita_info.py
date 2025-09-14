import re
import search_model
from collections import namedtuple

OperatorInfo = namedtuple('OperatorInfo',
                          ['qita_name', 'miao_shu', 'yong_tu', 'huode_fangshi', 'fen_lei'])


async def main(qita):
    qita_name, wikitext = await search_model.get_operator_wikitext(qita)

    if not wikitext:
        return None

    # 定义要查找的字段及对应的正则表达式
    fields = [
        ('miao_shu', r"\|描述\s*=\s*(.+)", lambda x: x.strip()),
        ('yong_tu', r"\|用途\s*=\s*(.+)", lambda x: x.strip()),
        ('huode_fangshi', r"\|获得方式\s*=\s*(.+)", lambda x: x.strip()),
        ('fen_lei', r"\|分类\s*=\s*(.+)", lambda x: x.strip())
    ]

    # 批量处理正则表达式查找和结果处理
    results = {}
    for field_name, pattern, process_func in fields:
        match = re.search(pattern, wikitext)
        if match:
            results[field_name] = process_func(match.group(1))
        else:
            results[field_name] = None

    return OperatorInfo(qita_name, results['miao_shu'], results['yong_tu'],
                        results['huode_fangshi'], results['fen_lei'])


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(main("娜仁图亚"))
    print(f"名称：{result.qita_name}")
    print(f"介绍：{result.miao_shu}")
    print(f"用途：{result.yong_tu}")
    print(f"获得方式：{result.huode_fangshi}")
    print(f"分类：{result.fen_lei}")
