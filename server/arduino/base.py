import requests

from ..config import config


def build_url(endpoint):
    ip = config["arduino"]["ip"]
    port = config["arduino"]["port"]
    return f"http://{ip}:{port}/{endpoint}"


def http_get(endpoint):
    return requests.get(
        build_url(endpoint), timeout=config["arduino"]["timeout"]
    ).json()


def http_post(endpoint, data):
    resp = requests.post(
        build_url(endpoint), timeout=config["arduino"]["timeout"], data=data
    )
    resp.raise_for_status()
    return resp
