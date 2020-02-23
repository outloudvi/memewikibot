import mwclient
from config import conf

site = mwclient.Site("meme.outv.im", "/")
site.login(conf["username"], conf["password"])
print("[wiki] Login succeed as", conf["username"])


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
