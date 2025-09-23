import re
from . import search_model
from collections import namedtuple

OperatorInfo = namedtuple('OperatorInfo',
                          ['other_thing_name', 'describe', 'yong_tu', 'get_manner', 'fen_lei'])

# 预编译字段正则表达式
FIELD_PATTERNS_OTHER = [
    ('describe', re.compile(r"\|描述\s*=\s*(.+)"), lambda x: x.strip()),
    ('yong_tu', re.compile(r"\|用途\s*=\s*(.+)"), lambda x: x.strip()),
    ('get_manner', re.compile(r"\|获得方式\s*=\s*(.+)"), lambda x: x.strip()),
    ('fen_lei', re.compile(r"\|分类\s*=\s*(.+)"), lambda x: x.strip())
]


async def clean_over_wiki(other_thing_name):
    other_thing_name = await search_model.search_wikitext(other_thing_name)
    other_thing_name, wikitext = await search_model.get_wikitext(other_thing_name)

    if not wikitext:
        return None

    # 批量处理正则表达式查找和结果处理
    results = {}
    for field_name, pattern, process_func in FIELD_PATTERNS_OTHER:
        match = pattern.search(wikitext)
        if match:
            results[field_name] = process_func(match.group(1))
        else:
            results[field_name] = None

    return OperatorInfo(other_thing_name, results['describe'], results['yong_tu'],
                        results['get_manner'], results['fen_lei'])


async def main(other_thing_name=None):
    if other_thing_name is None:
        other_thing_name = input("请输入名称：")
    # other_thing_name = "娜仁图亚的信物"
    """
    result含有的参数（按顺序）：
    other_thing_name, describe, yong_tu, get_manner, fen_lei
    """
    result = await clean_over_wiki(other_thing_name)
    if result:
        print(f"名称：{result.other_thing_name}")
        print(f"介绍：{result.describe}")
        print(f"用途：{result.yong_tu}")
        print(f"获得方式：{result.get_manner}")
        print(f"分类：{result.fen_lei}")
    else:
        print("未找到该物品的信息。")
