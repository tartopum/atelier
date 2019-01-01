import json
import os

_HERE = os.path.dirname(__file__)
_CONFIG_PATH = os.path.join(_HERE, "..", "config.json")

def read_input(title):
    val = input(title)
    while not val:
        print("Cannot be empty")
        val = input(title)
    return val


print("Web credentials:")
user = read_input("User:")
pwd = read_input("Password:")

with open(_CONFIG_PATH, "r") as f:
    cfg = json.load(f)

cfg["server"]["credentials"] = [user, pwd]

with open(_CONFIG_PATH, "w") as f:
    json.dump(cfg, f, indent=2)
