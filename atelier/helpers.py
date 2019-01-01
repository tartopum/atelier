from flask import request, url_for, redirect
from flask_httpauth import HTTPBasicAuth

from . import db
from .config import config


auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    user, pwd = config["server"]["credentials"]
    if user != username:
        return None
    return pwd


def redirect_url(default="home"):
    return request.args.get('next') or request.referrer or url_for(default)


def redirect_prev():
    return redirect(redirect_url())


def raise_alert(name, msg):
    db.add_alert(name, msg)
    # TODO: send SMS
    # Alert level:
    # 1. SMS
    # 2. Mail
