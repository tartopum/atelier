from flask import request, url_for, redirect

from . import db


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
