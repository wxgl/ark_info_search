import httpx
import asyncio
import re


async def get_public_recruitment_data():
    """异步获取所有可公开招募的干员数据。"""
    url = "https://prts.wiki/api.php"
    params = {
        "action": "cargoquery",
        "format": "json",
        "tables": "chara,char_obtain",
        "limit": "5000",
        "fields": "chara.profession,chara.position,chara.rarity,chara.tag,chara.cn",
        "where": "char_obtain.obtainMethod LIKE '%公开招募%'",
        "join_on": "chara._pageName=char_obtain._pageName"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            return [item["title"] for item in data.get("cargoquery", [])]

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        print(f"数据获取失败，请检查网络连接或API状态。错误: {e}")
        return None


async def main():
    """主函数，负责用户交互和数据处理。"""
    print("公招查询")
    user_input = input("请输入公招标签（用逗号分隔，如：治疗，重装）：")

    input_tags = [tag.strip() for tag in user_input.split('，') if tag.strip()]
    # 支持中英文逗号
    if not input_tags:
        input_tags = [tag.strip() for tag in user_input.split(',') if tag.strip()]

    if not input_tags:
        print("您没有输入任何标签。")
        return

    operators_data = await get_public_recruitment_data()

    if operators_data is None:
        return

    matched_operators = []
    matched_operators_all = []

    # 遍历所有干员数据，进行匹配
    for operator in operators_data:
        # 获取干员的标签字符串
        operator_tags_str = operator.get("tag", "")

        # 部分匹配：只要有一个标签匹配即可
        for tag in input_tags:
            # 使用正则表达式进行部分匹配
            if all(tag in operator_tags_str for tag in input_tags) and operator not in matched_operators_all:
                matched_operators_all.append(operator)
            if re.search(tag, operator_tags_str) and operator not in matched_operators:
                matched_operators.append(operator)

    # 按照输入标签的顺序显示结果
    if not matched_operators:
        print("未找到符合您所选标签的干员。")
    else:
        # 显示完全匹配的干员
        if matched_operators_all:
            print("\n找到以下完全匹配的干员：")
            for op_all in matched_operators_all:
                name = op_all.get("cn", "未知干员")
                rarity = "★" * (int(op_all.get("rarity", 0)) + 1)
                profession = op_all.get("profession", "未知职业")
                position = op_all.get("position", "未知位置")
                tags = op_all.get("tag", "无标签")

                print("-" * 10)
                print(f"干员: {name}")
                print(f"星级: {rarity}")
                print(f"职业: {profession}")
                print(f"位置: {position}")
                print(f"标签: {tags}")
        else:
            print("\n暂无完全匹配的干员。")
    # 按照输入标签的顺序显示部分匹配的干员
    print("\n找到以下部分匹配的干员：")
    for tag in input_tags:
        print(f"\n标签 '{tag}' 匹配的干员：")
        tag_matched_count = 0
        for op in matched_operators:
            operator_tags_str = op.get("tag", "")
            if re.search(tag, operator_tags_str) and not op in matched_operators_all:
                name = op.get("cn", "未知干员")
                rarity = "★" * (int(op.get("rarity", 0)) + 1)
                profession = op.get("profession", "未知职业")
                position = op.get("position", "未知位置")
                tags = op.get("tag", "无标签")

                print("-" * 10)
                print(f"干员: {name}")
                print(f"星级: {rarity}")
                print(f"职业: {profession}")
                print(f"位置: {position}")
                print(f"标签: {tags}")
                tag_matched_count += 1


if __name__ == "__main__":
    asyncio.run(main())
