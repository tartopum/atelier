import logging

from flask import request, url_for, redirect
from flask_httpauth import HTTPBasicAuth
import requests

from . import db
from .config import config


logger = logging.getLogger("atelier")
auth = HTTPBasicAuth()

ALERT_LEVEL_SMS = 2


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
            "msg": f'Controllino : "{msg}"',
        }
    )
    if resp.status_code != 200:
        logger.error(f"Cannot send alert SMS: {resp.status_code} {resp.text}")



def get_messages(conditions):
    m = []
    for val, cond_val, msg, url_name in conditions:
        if val == cond_val:
            m.append((msg, url_for(url_name)))
    return m


def make_message_getter(conditions, base_url_name=None):
    def get_cond_url_name(cond):
        try:
            return cond[3] or base_url_name
        except IndexError:
            return base_url_name

    def f(state):
        return get_messages([
            (state[cond[0]], cond[1], cond[2], get_cond_url_name(cond))
            for cond in conditions
        ])
    return f
