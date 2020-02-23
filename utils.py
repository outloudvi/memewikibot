import re

JISFW_LINE = re.compile(r'\{\{JISFW\|id=([0-9]+)\}\}')
ENTITIES_LINE = re.compile(r'\{\{Entities\|(.+)\}\}')
SOURCE_LINE = re.compile(r'\{\{Source\|(.+)\}\}')
CATEGORY_LINE = re.compile(r'\[\[Category:(.+)\]\]')
REDIRECT_LINE = re.compile(r'#redirect \[\[(.+)\]\]')


def parse_jisfw_text(text):
    tags = {
        "id": [],
        "entities": [],
        "categories": [],
        "source": ""
    }
    for i in text.split("\n"):
        sourceAlreadySet = False
        if REDIRECT_LINE.match(i):
            return {
                "redirect": REDIRECT_LINE.match(i).groups()[0]
            }
        elif JISFW_LINE.match(i):
            tags["id"].append(JISFW_LINE.match(i).groups()[0])
        elif ENTITIES_LINE.match(i):
            tags["entities"] = ENTITIES_LINE.match(i).groups()[0].split("|")
        elif CATEGORY_LINE.match(i):
            tags["categories"].append(CATEGORY_LINE.match(i).groups()[0])
        elif SOURCE_LINE.match(i) and not sourceAlreadySet:
            tags["source"] = SOURCE_LINE.match(i).groups()[0]
            sourceAlreadySet = True
    return tags
