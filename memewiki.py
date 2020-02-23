import mwclient
import json
from config import conf

site = mwclient.Site("meme.outv.im", "/")
site.login(conf["username"], conf["password"])
print("[wiki] Login succeed as", conf["username"])
sep = "\n<!-- TGBOT -->\n"


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


def commit_edit(obj, user):
    print(obj)
    if "action" not in obj:
        print("No action here")
        return
    print(user)
    page = site.pages[obj["pagename"]]
    if obj["action"] == "create_page":
        print("Creating", obj["pagename"])
        text = "{{{{JISFW|id={}}}}}\n{}[[Tag::{}|]]".format(
            obj["jisfw_id"], sep, obj["tag_to_add"])
        page.save(text, summary='Edit from {}'.format(user.full_name))
        print("Done")
    elif obj["action"] == "add_tag":
        print("Editing", obj["pagename"])
        page = site.pages[obj["pagename"]]
        text = page.text()
        if text.find(sep) != -1:
            idx = text.find(sep)
            prefix = text[0:idx]
            suffix = text[idx + len(sep):]
            text = prefix + "[[Tag::{}|]]".format(obj["tag_to_add"]) + suffix
        else:
            text += sep
            text += "[[Tag::{}]]".format(obj["tag_to_add"])
        page.save(text, summary='Edit from {}'.format(user.full_name))
        print("Done")
