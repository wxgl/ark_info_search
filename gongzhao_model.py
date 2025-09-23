import httpx
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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            recruitment_data_cache = [item["title"] for item in data.get("cargoquery", [])]
            return recruitment_data_cache

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        print(f"数据获取失败，请检查网络连接或API状态。错误: {e}")
        return None


async def main():
    """主函数，负责用户交互和数据处理。"""
    print("公招查询")
    user_input = input("请输入公招标签（用逗号分隔，如：治疗，防护）：")
    tags = re.split(r'[\s,，]+', user_input)
    input_tags = [tag.strip() for tag in tags if tag.strip()]

    if not input_tags:
        print("您没有输入任何标签。")
        return

    operators_data = await get_public_recruitment_data()

    if operators_data is None:
        return

    matched_operators_all = []
    matched_operators_single = {tag: [] for tag in input_tags}  # 每个标签下单独匹配的干员

    # 遍历所有干员数据，进行匹配
    for operator in operators_data:
        # 获取干员的标签字符串
        operator_tags_str = operator.get("tag", "")

        # 统计该干员匹配了多少个输入标签
        matched_tag_count = 0
        for tag in input_tags:
            if tag in operator_tags_str:
                matched_tag_count += 1

        # 完全匹配：干员同时具有所有输入标签
        if matched_tag_count == len(input_tags):
            matched_operators_all.append(operator)
        # 部分匹配：只匹配部分标签
        elif matched_tag_count > 0:
            # 对于每个匹配的标签，将该干员添加到对应的列表中
            for tag in input_tags:
                if tag in operator_tags_str:
                    matched_operators_single[tag].append(operator)

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

    # 按照输入标签的顺序显示单个标签匹配的干员
    print("\n找到以下单标签匹配的干员：")
    for tag in input_tags:
        operators = matched_operators_single[tag]
        print(f"\n标签 '{tag}' 匹配的干员：")

        # 从单标签匹配列表中排除那些也出现在完全匹配列表中的干员
        unique_operators = [op for op in operators if op not in matched_operators_all]

        if not unique_operators:
            print("无匹配干员")
            continue

        for op in unique_operators:
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
