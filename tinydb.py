import uuid
import json

db = {}


def write_tmp(data):
    id = str(uuid.uuid4())
    db[id] = data
    return id


def read_tmp(id):
    if id in db:
        return db[id]
    del db[id]
    return None


def save(filepath):
    global db
    with open(filepath, "w") as fp:
        json.dump(db, fp)


def load(filepath):
    global db
    with open(filepath) as fp:
        db = json.load(fp)


def read(item, domain="0"):
    if domain not in db:
        return None
    if item not in db[domain]:
        return None
    return db[domain][item]


def write(item, value, domain="0"):
    if domain not in db:
        db[domain] = {}
    db[domain][item] = value
