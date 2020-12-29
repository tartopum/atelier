from base64 import b64encode

from .base import *  # noqa
from . import fence, tank, workshop
from ..config import config


def configure():
    config.validate()
    credentials = b64encode(
        bytes(":".join(config["server"]["http_credentials"]), "utf8")
    ).decode("utf8")
    http_post(  # noqa
        "config_api",
        {
            "ip": config["server"]["ip"],
            "port": config["server"]["port"],
            "auth_header": f"Authorization: Basic {credentials}",
        },
    )
    fence.configure()
    tank.configure()
    workshop.configure()


def read_states():
    return {
        "fence": fence.read_state(),
        "tank": tank.read_state(),
        "workshop": workshop.read_state(),
    }
