import json
import os
import sys

_HERE = os.path.dirname(__file__)
_CONFIG_PATH = os.path.join(_HERE, "..", "config.json")

def read_input(title, required=True):
    val = input(title)
    while required and not val:
        print("Cannot be empty")
        val = input(title)
    return val


def store_config(section, key, val):
    with open(_CONFIG_PATH, "r") as f:
        cfg = json.load(f)

    cfg[section][key] = val

    with open(_CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def store_credentials(label, section, key, required=True):
    print(f"{label} (config.{section}.{key}):")
    user = read_input("User:", required=required)
    pwd = read_input("Password:", required=required)
    print("")
    store_config(section, key, [user, pwd])


if __name__ == "__main__":
    try:
        _CONFIG_PATH = sys.argv[1]
    except IndexError:
        print("Usage: python3 config.py <config.json-path>")
        sys.exit(1)

    store_credentials("Basic auth", "server", "http_credentials")
    store_credentials("SMS API Free mobile", "server", "sms_credentials", required=False)
    store_config("server", "db_backup", read_input("Database backup path:"))
