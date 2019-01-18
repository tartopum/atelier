import logging

from flask import request, url_for, redirect
from flask_httpauth import HTTPBasicAuth
import requests

from . import db
from .config import config


logger = logging.getLogger("flask.app")
auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    user, pwd = config["server"]["http_credentials"]
    if user != username:
        return None
    return pwd


def redirect_url(default="home"):
    return request.args.get('next') or request.referrer or url_for(default)


def redirect_prev():
    return redirect(redirect_url())


def raise_alert(name, msg, level):
    db.add_alert(name, msg)
    if level < 2:
        return
    user, password = config["server"]["sms_credentials"]
    if not user or not password:
        return
    resp = requests.get(
        "https://smsapi.free-mobile.fr/sendmsg",
        params={
            "user": user,
            "pass": password,
            "msg": f'La Controllino dit : "{msg}"',
        }
    )
    if resp.status_code != 200:
        logger.error(f"Cannot send alert SMS: {resp.status_code} {resp.text}")
