import datetime as dt
import itertools
import json
import logging

from flask import Flask, render_template, request, url_for
from flask_wtf import CSRFProtect

from . import routes
from .auth import auth
from .routes.base import arduino_get_route
from .. import alerts, arduino, db
from .. import config

logger = logging.getLogger("atelier")

config.validate()

app = Flask(__name__)

app.secret_key = config.get("server", "secret_key").encode("utf-8")
app.logger = logger

app.register_blueprint(routes.config.blueprint, url_prefix="/config")
app.register_blueprint(routes.fence.blueprint, url_prefix="/cloture")
app.register_blueprint(routes.monitoring.blueprint, url_prefix="/debug")
app.register_blueprint(routes.orchard.blueprint, url_prefix="/verger")
app.register_blueprint(routes.tank.blueprint, url_prefix="/eau")
app.register_blueprint(routes.workshop.blueprint, url_prefix="/atelier")

csrf = CSRFProtect(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db.db_path()
db.db.init_app(app)


ALERT_NAME_TO_URL = {
    "fence": "fence.fence_route",
    "monitoring": "monitoring.monitoring_route",
    "monitoring_debug": ("monitoring.monitoring_route", "debug"),
    "monitoring_rpi": ("monitoring.monitoring_route", "rpi"),
    "power_supply": ("workshop.workshop_route", "alimentation"),
    "tank": "tank.tank_route",
    "workshop": "workshop.workshop_route",
}


def parse_alert(a):
    url_name = ALERT_NAME_TO_URL.get(a.name)
    if url_name is None:
        url = None
    elif isinstance(url_name, str):
        url = url_for(url_name)
    else:
        url_name, anchor = url_name
        url = url_for(url_name) + "#" + anchor
    return (a.message, url)


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
    def alert_day_label(date):
        delta_days = (dt.date.today() - date.date()).days
        if delta_days == 0:
            return "Aujourd'hui"
        prefix = f"Il y a {delta_days} jour{'s' if delta_days > 1 else ''}"
        date_str = date.strftime("%d/%m/%Y")
        return f"{prefix} ({date_str})"

    past_alerts = db.list_alerts(n_days_ago=7)
    grouped_alerts = itertools.groupby(
        past_alerts,
        lambda x: alert_day_label(x[0])
    )
    states = arduino.read_states()
    return render_template(
        "home.html",
        no_alerts=(len(past_alerts) < 1),
        alerts=grouped_alerts,
        errors=list(map(parse_alert, alerts.get_errors(states))),
        warnings=list(map(parse_alert, alerts.get_warnings(states))),
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
        alerts.raise_alert(name, msg, level)
    return ""
