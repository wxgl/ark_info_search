import httpx
import re

# 创建全局的httpx客户端，用于连接池和复用连接
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0),
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=50)
)


async def get_wikitext(name: str):
    """异步获取页面的wikitext内容"""
    url = "https://prts.wiki/api.php"
    params1 = {
        "action": "query",
        "list": "search",
        "srsearch": name,
        "format": "json"
    }
    search_result = await http_client.get(url, params=params1)
    search_data = search_result.json()["query"]["search"]
    search_data = [item["title"] for item in search_data]
    """支持省略字符串输入:
    输入：破茧之梦
    匹配：“破茧之梦”
    """
    search_filtered = [re.sub(r'[^\u4e00-\u9fff\w]', '', item) for item in search_data]
    name_filtered = re.sub(r'[^\u4e00-\u9fff\w]', '', name)
    # 使用enumerate避免重复查找索引
    for i, r in enumerate(search_filtered):
        if r == name_filtered:
            name = search_data[i]
            break
    params2 = {
        "action": "query",
        "prop": "revisions",
        "titles": name,
        "rvprop": "content",
        "format": "json",
        "redirects": ""
    }
    response = await http_client.get(url, params=params2)
    response.raise_for_status()
    data = response.json()

    pages = data["query"]["pages"]
    # 获取第一个页面的信息，因为API返回的page id是动态的
    page_id = next(iter(pages))
    page_data = pages[page_id]

    name_out = page_data["title"]
    # 检查页面是否存在或是否包含修订版本
    if "revisions" not in page_data or not page_data["revisions"]:
        # 页面不存在或没有修订版本，返回None
        wikitext = None
    else:
        wikitext = page_data["revisions"][0]["*"]
    return name_out, wikitext


async def get_operator_image(name: str, skin):
    """异步获取干员的image，默认为精二皮"""

    if "时装" in skin:
        skin = skin.replace("时装", "skin")
    name = f"文件:立绘 {name} {skin}.png"
    return await get_images_url([name])


async def get_images_url(image_titles: list):
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

    image_url_list = []
    pages = data["query"]["pages"]
    for page_id in pages:
        page_data = pages[page_id]
        if "imageinfo" in page_data and page_data["imageinfo"]:
            image_url = page_data["imageinfo"][0]["url"]
            image_url_list.append(image_url)

    return image_url_list


async def get_operator_info_concurrently(name: str, skin="2"):
    """并发获取干员信息和图片，提高处理速度"""
    try:
        name_out, wikitext = await get_wikitext(name)
        image_url = await get_operator_image(name, skin)
        return name_out, wikitext, image_url
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        print(f"获取干员信息失败: {e}")
        return None


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
