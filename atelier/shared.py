import functools

from flask import abort, current_app as app, render_template
import requests


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
    # TODO: check status
    requests.post(
        build_arduino_url(endpoint),
        timeout=app.config["TIMEOUT"],
        data=data
    )
