import requests


def search_operator(name):
    url = "https://prts.wiki/api.php"
    params = {"action": "opensearch", "search": name, "format": "json"}
    return requests.get(url, params=params).json()


def get_operator_wikitext(name):
    url = "https://prts.wiki/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": name,
        "rvprop": "content",
        "format": "json"
    }
    data = requests.get(url, params=params).json()
    pages = data["query"]["pages"]
    name = list(pages.values())[0]["title"]
    wikitext = list(pages.values())[0]["revisions"][0]["*"]
    return name, wikitext
