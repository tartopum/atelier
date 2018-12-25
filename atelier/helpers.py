import functools
import json

from flask import abort, current_app as app, render_template, request, url_for, redirect
import requests


def redirect_url(default="home"):
    return request.args.get('next') or request.referrer or url_for(default)


def build_arduino_url(endpoint):
    ip = app.config["ARDUINO_IP"]
    port = app.config["ARDUINO_PORT"]
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
    body = json.dumps(data, indent=2)
    try:
        resp = requests.post(
            build_arduino_url(endpoint),
            timeout=app.config["TIMEOUT"],
            data=data
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        logs = f"POST {e.request.url}\n{body}"
        return render_template("arduino_404.html", logs=logs), 500

    if resp.status_code != 200:
        req_logs = f"POST {resp.request.url}\n{body}"
        resp_logs = resp.text
        return render_template("arduino_400.html", req=req_logs, resp=resp_logs), 500

    return redirect(redirect_url())
