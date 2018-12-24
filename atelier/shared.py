from flask import abort, current_app as app
import requests


def build_arduino_url(endpoint):
    ip = app.config["ARDUINO_IP"]
    port = app.config["ARDUINO_PORT"]
    return f"http://{ip}:{port}/{endpoint}"


def post_arduino(endpoint, data):
    # TODO: check status
    try:
        requests.post(
            build_arduino_url(endpoint),
            timeout=app.config["TIMEOUT"],
            data=data
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return render_template("arduino_404.html", url=e.request.url), 500
