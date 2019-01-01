import functools
import json

from flask import render_template
import requests
from requests.exceptions import ConnectionError, ReadTimeout, HTTPError

from .config import config
from .helpers import auth, redirect_prev


def read_state(x):
    data = requests.get(
        build_url(x.arduino_endpoint),
        timeout=config["arduino"]["timeout"]
    ).json()
    for k, v in data.items():
        x.state[k] = v
    return x.state


def build_url(endpoint):
    ip = config["arduino"]["ip"]
    port = config["arduino"]["port"]
    return f"http://{ip}:{port}/{endpoint}"


def get_route(f):
    @auth.login_required
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (ConnectionError, ReadTimeout) as e:
            logs = f"GET {e.request.url}"
            return render_template("arduino_404.html", logs=logs), 500
    functools.update_wrapper(decorated, f)
    return decorated


def post(endpoint, data):
    resp = requests.post(
        build_url(endpoint),
        timeout=config["arduino"]["timeout"],
        data=data
    )
    resp.raise_for_status()


def post_route(func):
    @auth.login_required
    def decorated(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
        except (ConnectionError, ReadTimeout) as e:
            req_logs = f"POST {e.request.url} {e.request.body}"
            return render_template("arduino_404.html", logs=req_logs), 500
        except HTTPError as e:
            req_logs = f"POST {e.request.url} {e.request.body}"
            resp_logs = e.response.text
            return (
                render_template("arduino_400.html", req=req_logs, resp=resp_logs), 500
            )

        if resp is not None:
            return resp
        return redirect_prev()

    functools.update_wrapper(decorated, func)
    return decorated


def register_post_route(func, app, *route_args, **route_kwargs):
    @post_route
    def route_func(*args, **kwargs):
        return func(*args, **kwargs)

    route_func.__name__ = func.__name__
    app.route(*route_args, **route_kwargs)(route_func)
