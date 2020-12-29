import logging

import requests

from .config import config


logger = logging.getLogger("atelier")


def send_sms(msg):
    user, password = config["server"]["sms_credentials"]
    if not user or not password:
        return
    resp = requests.get(
        "https://smsapi.free-mobile.fr/sendmsg",
        params={"user": user, "pass": password, "msg": f'Controllino : "{msg}"'},
    )
    if resp.status_code != 200:
        logger.error("Cannot send SMS: %s %s", resp.status_code, resp.text)
