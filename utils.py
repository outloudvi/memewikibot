import re

JISFW_LINE = re.compile(r'\{\{JISFW\|id=([0-9]+)\}\}')
CATEGORY_LINE = re.compile(r'\[\[Category:(.+)\]\]')
REDIRECT_LINE = re.compile(r'#redirect \[\[(.+)\]\]')


def parse_jisfw_text(text):
    tags = {
        "id": [],
        "categories": [],
    }
    for i in text.split("\n"):
        if REDIRECT_LINE.match(i):
            return {
                "redirect": REDIRECT_LINE.match(i).groups()[0]
            }
        elif JISFW_LINE.match(i):
            tags["id"].append(JISFW_LINE.match(i).groups()[0])
        elif CATEGORY_LINE.match(i):
            tags["categories"].append(CATEGORY_LINE.match(i).groups()[0])
    return tags
