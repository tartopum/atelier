from flask import Blueprint, render_template, request

from .base import arduino_post_route, flash_success, redirect_prev
from .. import forms
from ... import arduino, scheduler
from ...config import config


blueprint = Blueprint("config", __name__)


@blueprint.route("/", methods=["GET", "POST"])
@arduino_post_route
def config_route():
    config_forms = forms.ConfigForms(request.form)
    if request.method == "POST" and config_forms.validate():
        config_forms.populate_config()
        arduino.configure()
        config.save()

        scheduler.lunch_job.at = config["alarm"]["lunch"]
        scheduler.night_job.at = config["alarm"]["night"]
        scheduler.tank_job.every = config["tank"]["stats_collection_period"]

        flash_success("La configuration a été mise à jour.")
        return redirect_prev()

    return render_template(
        "config.html",
        forms=config_forms,
        form_errors=any(form.errors for _, form in config_forms.values()),
    )
