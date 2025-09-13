import httpx


async def search_operator(name: str):
    """异步搜索干员名称"""
    url = "https://prts.wiki/api.php"
    params = {"action": "opensearch", "search": name, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()  # 如果请求失败则抛出异常
        return response.json()


async def get_operator_wikitext(name: str):
    """异步获取页面的wikitext内容"""
    url = "https://prts.wiki/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": name,
        "rvprop": "content",
        "format": "json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()  # 如果请求失败则抛出异常
        data = response.json()

    pages = data["query"]["pages"]
    # 获取第一个页面的信息，因为API返回的page id是动态的
    page_id = next(iter(pages))
    page_data = pages[page_id]

    # 检查页面是否存在或是否包含修订版本
    if "revisions" not in page_data or not page_data["revisions"]:
        # 可以根据需要返回一个更友好的提示或者None
        return None, None

    name_out = page_data["title"]
    wikitext = page_data["revisions"][0]["*"]
    return name_out, wikitext