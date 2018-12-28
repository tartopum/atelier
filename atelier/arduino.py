import functools
import json

from flask import render_template
import requests
from requests.exceptions import ConnectionError, ReadTimeout, HTTPError

from . import config
from .helpers import redirect_prev

config.schema.add_section("arduino")
config.schema.add_ip("arduino", "ip")
config.schema.add_port("arduino", "port")
config.schema.add_int("arduino", "timeout", min=1, max=10)


def configure():
    config.validate()
    pass # TODO


def read_state(x):
    data = requests.get(
        build_url(x.arduino_endpoint),
        timeout=config.config["arduino"]["timeout"]
    ).json()
    for k, v in data.items():
        x.state[k] = v
    return x.state


def build_url(endpoint):
    ip = config.config["arduino"]["ip"]
    port = config.config["arduino"]["port"]
    return f"http://{ip}:{port}/{endpoint}"


def get_route(f):
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
        timeout=config.config["arduino"]["timeout"],
        data=data
    )
    resp.raise_for_status()


def register_post_route(func, app, *route_args, **route_kwargs):
    def route_func(*args, **kwargs):
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

    route_func.__name__ = func.__name__
    app.route(*route_args, **route_kwargs)(route_func)
