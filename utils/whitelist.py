import json
import time
import os

WHITELIST_FILE = "data/whitelist.json"

def load_wl():
    if not os.path.exists(WHITELIST_FILE):
        return {}
    with open(WHITELIST_FILE, "r") as f:
        return json.load(f)

def save_wl(wl):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(wl, f, indent=4)

def add_wl(user_id: int, duration_seconds: int):
    wl = load_wl()
    wl[str(user_id)] = {
        "expires_at": int(time.time()) + duration_seconds
    }
    save_wl(wl)

def remove_wl(user_id: int):
    wl = load_wl()
    wl.pop(str(user_id), None)
    save_wl(wl)

def is_wl_valid(user_id: int):
    wl = load_wl()
    entry = wl.get(str(user_id))

    if not entry:
        return False

    if entry["expires_at"] < time.time():
        wl.pop(str(user_id))
        save_wl(wl)
        return False

    return True
