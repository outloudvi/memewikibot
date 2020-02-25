import re

JISFW_LINE = re.compile(r'\{\{JISFW(.+)\}\}')
REDIRECT_LINE = re.compile(r'#redirect \[\[(.+)\]\]')


def parse_jisfw_text(text):
    tags = {
        "id": []
    }
    for i in text.split("\n"):
        if REDIRECT_LINE.match(i):
            return {
                "redirect": REDIRECT_LINE.match(i).groups()[0]
            }
        elif JISFW_LINE.match(i):
            matches = JISFW_LINE.match(i).groups()[0].split("|")
            for i in matches:
                target = re.sub(r".+=", "", i)
                if target.isdigit():
                    tags["id"].append(target)
    return tags


def gen_wiki_jisfw_link(meme_id):
    return "[查看原文]({}) | [Wiki 页面]({})".format("https://t.me/JISFW/" + meme_id, "https://meme.outv.im/wiki/JISFW:" + meme_id)
