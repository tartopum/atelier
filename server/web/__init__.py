import itertools
import json
import logging

from flask import Flask, render_template, request

from . import routes
from .alerts import get_errors, get_warnings
from .auth import auth
from .routes.base import arduino_get_route
from .. import arduino, db
from ..alerts import raise_alert
from ..config import config

logger = logging.getLogger("atelier")

app = Flask(__name__)

app.secret_key = config["server"]["secret_key"].encode("utf-8")

app.register_blueprint(routes.config.blueprint, url_prefix="/config")
app.register_blueprint(routes.fence.blueprint, url_prefix="/cloture")
app.register_blueprint(routes.monitoring.blueprint, url_prefix="/debug")
app.register_blueprint(routes.tank.blueprint, url_prefix="/eau")
app.register_blueprint(routes.workshop.blueprint, url_prefix="/atelier")


@app.after_request
def after_request(response):
    if 400 <= response.status_code < 600:
        app.logger.warning(
            f"{request.remote_addr} got {response.status_code} for {request.url}:\n"
            f"\t* Request headers: {request.headers}\n"
            f"\t* Request content: {request.data}\n"
            f"\t* Request content len: {len(request.data)}\n"
            f"\t* Response: {response.response}"
        )
    return response


@app.route("/")
@arduino_get_route
def home_route():
    alerts = db.list_alerts(n_days_ago=7)
    grouped_alerts = itertools.groupby(alerts, lambda x: x[0].strftime("%A %d %B"))
    states = arduino.read_states()
    return render_template(
        "home.html",
        no_alerts=(len(alerts) < 1),
        alerts=grouped_alerts,
        errors=get_errors(states),
        warnings=get_warnings(states),
    )


@app.route("/send_config")
def send_config_route():
    # A route for the Arduino to ask for API config
    arduino.configure()
    return ""


@app.route("/alert", methods=["POST"])
@auth.login_required
def receive_alert():
    try:
        data = request.get_json()
        name = data["name"]
        msg = data["message"]
        level = data["level"]
    except (json.decoder.JSONDecodeError, KeyError) as e:
        logger.error("Invalid alert format", exc_info=e)
        return f"{e.__class__.__name__}: {e}", 500
    else:
        raise_alert(name, msg, level)
    return ""
