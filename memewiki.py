import mwclient
import json
from config import conf

site = mwclient.Site("meme.outv.im", "/")
site.login(conf["username"], conf["password"])
print("[wiki] Login succeed as", conf["username"])


def search_smw_query(search_string):
    data = site.api("ask", query=search_string)
    results = data.get("query").get("results")
    meta = {
        "count": data.get("query").get("meta").get("count"),
        "time": data.get("query").get("meta").get("time"),
        "offset": data.get("query").get("meta").get("offset")
    }
    result_list = list(results)
    return {
        "meta": meta,
        "results": result_list
    }


def get_smw_object(title, ns=0):
    data = site.api("smwbrowse", browse="subject",
                    params=json.dumps({"subject": title, "ns": ns}))
    properties = data.get("query").get("data")
    ret = {}
    for prop in properties:
        retpart = []
        key = prop.get("property")
        for value in prop.get("dataitem"):
            retpart.append(dict(value))
        ret[key] = retpart
    return ret


def get_property_of(title, prop, ns=0):
    obj = get_smw_object(title, ns)
    if prop in obj:
        return list(map(lambda x: x["item"], obj[prop]))
    return []


def get_raw_page(title):
    print("[wiki] Fetching", title)
    page = site.pages[title]
    if page.exists:
        print("[wiki]", title, "is found")
        return page
    else:
        print("[wiki]", title, "is not found")
        return None


def get_raw_text(title):
    page = get_raw_page(title)
    if page is None:
        return None
    else:
        return page.text()
