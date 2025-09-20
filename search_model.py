import httpx
import asyncio

# 创建全局的httpx客户端，用于连接池和复用连接
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0),
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=20)
)


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
    response = await http_client.get(url, params=params)
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
    # return wikitext
    return name_out, wikitext


async def get_operator_image(name: str, skin):
    """异步获取干员的image，默认为精二皮"""

    if "时装" in skin:
        skin = skin.replace("时装", "skin")
    name = f"文件:立绘 {name} {skin}.png"
    url = "https://prts.wiki/api.php"
    params = {
        "action": "query",
        "prop": "imageinfo",
        "iiprop": "url",
        "titles": name,
        "format": "json"
    }
    response = await http_client.get(url, params=params)
    response.raise_for_status()  # 如果请求失败则抛出异常
    data = response.json()
    # 获取图片的URL
    image_url = None
    pages = data["query"]["pages"]
    for page_id in pages:
        page_data = pages[page_id]
        if "imageinfo" in page_data and page_data["imageinfo"]:
            image_url = page_data["imageinfo"][0]["url"]
            break
    return image_url


async def get_images_info(image_titles: list):
    """批量获取图片的详细信息"""
    if not image_titles:
        return []

    url = "https://prts.wiki/api.php"
    # 将图片标题列表转换为管道分隔的字符串
    titles_str = "|".join([img["title"] if isinstance(img, dict) else img for img in image_titles])

    params = {
        "action": "query",
        "titles": titles_str,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    response = await http_client.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    image_info_list = []
    pages = data["query"]["pages"]
    for page_id in pages:
        page_data = pages[page_id]
        if "imageinfo" in page_data and page_data["imageinfo"]:
            image_info = page_data["imageinfo"][0]
            image_info["title"] = page_data["title"]
            image_info_list.append(image_info)

    return image_info_list


async def get_operator_info_concurrently(name: str, skin):
    """并发获取干员信息和图片，提高处理速度"""
    # 并发执行获取wikitext和图片的请求
    wikitext_task = asyncio.create_task(get_operator_wikitext(name))
    image_task = asyncio.create_task(get_operator_image(name,  skin))

    # 等待两个任务完成
    name_out, wikitext = await wikitext_task
    image_url = await image_task

    return name_out, wikitext, image_url


# 程序退出时关闭http客户端
async def close_http_client():
    """
    异步关闭HTTP客户端，避免资源泄露
    """
    try:
        await http_client.aclose()
    except Exception:
        # 忽略关闭时的任何异常
        pass
