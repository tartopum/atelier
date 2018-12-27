import functools
import json

from flask import abort, render_template, request, url_for, redirect
import requests

from .config import config


def redirect_url(default="home"):
    return request.args.get('next') or request.referrer or url_for(default)


def build_arduino_url(endpoint):
    ip = config["arduino"]["ip"]
    port = config["arduino"]["port"]
    return f"http://{ip}:{port}/{endpoint}"


def arduino_get(f):
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            logs = f"GET {e.request.url}"
            return render_template("arduino_404.html", logs=logs), 500
    functools.update_wrapper(decorated, f)
    return decorated


def post_arduino(endpoint, data):
    resp = requests.post(
        build_arduino_url(endpoint),
        timeout=config["arduino"]["timeout"],
        data=data
    )
    resp.raise_for_status()
    return resp


def register_arduino_route(func, app, route):
    def route_func(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            logs = f"POST {e.request.url} {e.request.body}"
            return render_template("arduino_404.html", logs=logs), 500
        except requests.exceptions.HTTPError:
            req_logs = f"POST {resp.request.url} {resp.request.body}"
            resp_logs = resp.text
            return render_template("arduino_400.html", req=req_logs, resp=resp_logs), 500

        return redirect(redirect_url())
    route_func.__name__ = func.__name__
    app.route(route)(route_func)
