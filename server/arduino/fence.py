from .base import http_get, http_post


def read_state():
    return http_get("fence")


def configure():
    return


def activate(activated):
    return http_post("fence", {"activated": int(activated)})


def command(is_on):
    return http_post("fence", {"state": int(is_on)})
