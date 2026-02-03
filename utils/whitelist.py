import json, time, os

FILE = "data/whitelist.json"

def load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save(wl):
    with open(FILE, "w") as f:
        json.dump(wl, f, indent=2)

def add(user_id: int, days: int):
    wl = load()
    wl[str(user_id)] = int(time.time()) + days * 86400
    save(wl)

def remove(user_id: int):
    wl = load()
    wl.pop(str(user_id), None)
    save(wl)

def is_valid(user_id: int):
    wl = load()
    exp = wl.get(str(user_id))
    if not exp:
        return False
    if exp < time.time():
        wl.pop(str(user_id))
        save(wl)
        return False
    return True
