import json

from flask import Blueprint, redirect, render_template, Response, send_file, url_for

from .base import arduino_get_route
from ..auth import auth
from ... import arduino, config, db, monitoring, scheduler


blueprint = Blueprint("monitoring", __name__)


@blueprint.route("/")
@arduino_get_route
def monitoring_route():
    states = {
        "clôture": arduino.fence.read_state(),
        "atelier": arduino.workshop.read_state(),
        "eau": arduino.tank.read_state(),
    }
    states["api"] = arduino.http_get("config_api")

    for k, v in states.items():
        states[k] = json.dumps(v, indent=2)

    return render_template(
        "monitoring.html",
        states=states,
        debug=monitoring.is_debug_mode,
        debug_period=config.get("server", "debug_period"),
        logs=list(monitoring.parse_logs(config.ATELIER_LOG_PATH)),
        scheduler_logs=list(monitoring.parse_logs(config.SCHEDULER_LOG_PATH)),
        rpi=dict(
            disk_usage=monitoring.get_disk_usage(),
            cpu_percent=monitoring.get_cpu_percent(),
            cpu_temp=monitoring.get_cpu_temperature(),
            cpu_freq=monitoring.get_cpu_freq(),
            virtual_memory=monitoring.get_virtual_memory(),
        ),
    )


@blueprint.route("/debug/<int:activated>")
@arduino_get_route
def set_debug_mode_route(activated):
    monitoring.is_debug_mode = bool(activated)
    # Does not work in debug mode as the Flask dev server instanciates multiple
    # schedules and the one updated here may not be the one called in scheduler.run().
    scheduler.jobs["debug"].every = (
        config.get("server", "debug_period") if monitoring.is_debug_mode else None
    )
    if monitoring.is_debug_mode:
        # Empty the log file first
        open(config.CONTROLLINO_LOG_PATH, "w").close()
    return redirect(url_for("monitoring.monitoring_route", _anchor="debug"))


@blueprint.route("/download/controllino")
@auth.login_required
def download_controllino_debug_route():
    rows = monitoring.controllino_logs_to_csv()
    csv = "\n".join([",".join(map(str, row)) for row in rows])
    return Response(
        csv,
        mimetype="text/csv",
        headers={
            "Content-disposition": "attachment; filename=monitoring_controllino.csv"
        },
    )


@blueprint.route("/download/db")
@auth.login_required
def download_db_route():
    return send_file(
        db.db_path(),
        mimetype="application/octet-stream",
        as_attachment=True,
        attachment_filename="atelier.sqlite3",
    )
