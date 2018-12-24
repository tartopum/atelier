import functools

from flask import abort, current_app as app, render_template, request, url_for, redirect
import requests


def redirect_url(default="home"):
    return request.args.get('next') or request.referrer or url_for(default)


def build_arduino_url(endpoint):
    ip = app.config["ARDUINO_IP"]
    port = app.config["ARDUINO_PORT"]
    return f"http://{ip}:{port}/{endpoint}"


def arduino_req_route(f):
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            return render_template("arduino_404.html", url=e.request.url), 500
    functools.update_wrapper(decorated, f)
    return decorated


@arduino_req_route
def post_arduino(endpoint, data):
    requests.post(
        build_arduino_url(endpoint),
        timeout=app.config["TIMEOUT"],
        data=data
    )
    return redirect(redirect_url())
