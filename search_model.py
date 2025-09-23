import httpx
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建全局的httpx客户端，用于连接池和复用连接
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0),
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=50)
)


async def search_wikitext(name: str):
    """异步获取页面的wikitext内容"""
    url = "https://prts.wiki/api.php"
    params1 = {
        "action": "query",
        "list": "search",
        "srsearch": name,
        "format": "json"
    }
    try:
        search_result = await http_client.get(url, params=params1)
        search_result.raise_for_status()
        search_data = search_result.json()["query"]["search"]
        search_data = [item["title"] for item in search_data]
    except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
        logger.error(f"搜索请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"搜索处理失败: {e}")
        return None
    # 如果搜索结果为空，直接返回None
    if not search_data:
        return None
    """支持省略字符串输入:
    输入：破茧之梦
    匹配：“破茧之梦”
    """
    search_filtered = [re.sub(r'[^\u4e00-\u9fff\w]', '', item) for item in search_data]
    name_filtered = re.sub(r'[^\u4e00-\u9fff\w]', '', name)
    # 使用enumerate避免重复查找索引
    for i, r in enumerate(search_filtered):
        if r == name_filtered:
            return search_data[i]
    # 若未找到精确匹配，则选取包含该字段的最短项
    matching_items = []
    for i, r in enumerate(search_filtered):
        if name_filtered in r:
            matching_items.append((len(r), search_data[i]))
    # 如果有包含该字段的项，返回其中最短的
    if matching_items:
        matching_items.sort(key=lambda x: x[0])  # 按长度排序
        shortest_item = matching_items[0][1]
        print(f"未找到精确匹配项，使用包含该字段的最短项: {shortest_item}")
        return shortest_item


async def get_wikitext(name: str):
    url = "https://prts.wiki/api.php"
    params2 = {
        "action": "query",
        "prop": "revisions",
        "titles": name,
        "rvprop": "content",
        "format": "json",
        "redirects": "1"  # 启用重定向
    }
    try:
        response = await http_client.get(url, params=params2)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
        logger.error(f"获取页面内容失败: {e}")
        return name, None
    except Exception as e:
        logger.error(f"页面内容处理失败: {e}")
        return name, None
    pages = data["query"]["pages"]
    # 获取第一个页面的信息，因为API返回的page id是动态的
    page_id = next(iter(pages))
    page_data = pages[page_id]

    name_out = page_data.get("title", name)
    # 检查页面是否存在或是否包含修订版本
    if "revisions" not in page_data or not page_data["revisions"]:
        # 页面不存在或没有修订版本，返回None
        wikitext = None
    else:
        wikitext = page_data["revisions"][0]["*"]
    return name_out, wikitext


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
    try:
        response = await http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
        logger.error(f"获取图片信息失败: {e}")
        return []
    except Exception as e:
        logger.error(f"图片信息处理失败: {e}")
        return []
    image_url_list = []
    pages = data["query"]["pages"]
    for page_id in pages:
        page_data = pages[page_id]
        if "imageinfo" in page_data and page_data["imageinfo"]:
            image_url = page_data["imageinfo"][0]["url"]
            image_url_list.append(image_url)

    return image_url_list


# 程序退出时关闭http客户端
async def close_http_client():
    """
    异步关闭HTTP客户端，避免资源泄露
    """
    global http_client
    try:
        await http_client.aclose()
        logger.info("HTTP客户端已关闭")
    except RuntimeError as e:
        # Windows系统上可能会出现"Event loop is closed"错误，这是正常的
        if "Event loop is closed" not in str(e):
            logger.error(f"关闭HTTP客户端时出错: {e}")
    except Exception as e:
        logger.error(f"关闭HTTP客户端时发生未知错误: {e}")
