import json
import os

import requests
from requests.auth import HTTPBasicAuth

HERE = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(HERE, "..", "config.json")


def get_auth():
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)["server"]
    return HTTPBasicAuth(*cfg["http_credentials"])


def send(name, msg, level, ip, port):
    requests.post(
        f"http://{ip}:{port}/alert",
        json={"name": name, "message": msg, "level": level},
        auth=get_auth(),
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--msg", default="")
    parser.add_argument("--level", type=int, default=2)
    parser.add_argument("--ip", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    send(args.name, args.msg, args.level, args.ip, args.port)
