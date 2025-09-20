import re
import search_model
import asyncio
from collections import namedtuple

OperatorInfo = namedtuple('OperatorInfo',
                          ['qita_name', 'miao_shu', 'yong_tu', 'huode_fangshi', 'fen_lei'])

# 预编译字段正则表达式
FIELD_PATTERNS_QITA = [
    ('miao_shu', re.compile(r"\|描述\s*=\s*(.+)"), lambda x: x.strip()),
    ('yong_tu', re.compile(r"\|用途\s*=\s*(.+)"), lambda x: x.strip()),
    ('huode_fangshi', re.compile(r"\|获得方式\s*=\s*(.+)"), lambda x: x.strip()),
    ('fen_lei', re.compile(r"\|分类\s*=\s*(.+)"), lambda x: x.strip())
]


async def clean_over_wiki(qita):
    qita_name, wikitext = await search_model.get_operator_wikitext(qita)

    if not wikitext:
        return None

    # 批量处理正则表达式查找和结果处理
    results = {}
    for field_name, pattern, process_func in FIELD_PATTERNS_QITA:
        match = pattern.search(wikitext)
        if match:
            results[field_name] = process_func(match.group(1))
        else:
            results[field_name] = None

    return OperatorInfo(qita_name, results['miao_shu'], results['yong_tu'],
                        results['huode_fangshi'], results['fen_lei'])


async def main(qita=None):
    if qita is None:
        qita = input("请输入名称：")
    # qita = "娜仁图亚的信物"
    """
    result含有的参数（按顺序）：
    qita_name, miao_shu, yong_tu, huode_fangshi, fen_lei
    """
    result = await clean_over_wiki(qita)
    if result:
        print(f"名称：{result.qita_name}")
        print(f"介绍：{result.miao_shu}")
        print(f"用途：{result.yong_tu}")
        print(f"获得方式：{result.huode_fangshi}")
        print(f"分类：{result.fen_lei}")
    else:
        print("未找到该物品的信息。")


if __name__ == "__main__":
    async def run_main():
        try:
            await main("娜仁图亚的信物")
        finally:
            # 确保关闭HTTP客户端
            await search_model.close_http_client()
    
    asyncio.run(run_main())
