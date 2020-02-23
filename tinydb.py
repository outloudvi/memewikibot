import uuid

db = {}

def write(data):
    id = str(uuid.uuid4())
    db[id] = data
    return id

def read(id):
    if id in db:
        return db[id]
    return None

def read_once(id):
    ret = read(id)
    del db[id]
    return ret