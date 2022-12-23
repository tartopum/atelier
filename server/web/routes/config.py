from flask import Blueprint, render_template, request

from .base import arduino_post_route, flash_success, redirect_prev
from .. import forms
from ... import arduino, config, scheduler


blueprint = Blueprint("config", __name__)


@blueprint.route("/", methods=["GET", "POST"])
@arduino_post_route
def config_route():
    config_forms = forms.ConfigForms(request.form)
    if request.method == "POST" and config_forms.validate():
        config_forms.populate_config()
        arduino.configure()
        config.save()

        scheduler.jobs["lunch"].at = config.get("alarm", "lunch")
        scheduler.jobs["night"].at = config.get("alarm", "night")
        scheduler.jobs["tank"].every = config.get("tank", "stats_collection_period")

        flash_success("La configuration a été mise à jour.")
        return redirect_prev()

    return render_template(
        "config.html",
        forms=config_forms,
        form_errors=any(form.errors for _, form in config_forms.values()),
    )
