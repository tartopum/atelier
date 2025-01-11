import io

from flask import Blueprint, render_template, redirect, url_for, request
from openpyxl import load_workbook

from .base import flash_error
from ... import db
from .. import forms

blueprint = Blueprint("orchard", __name__)


@blueprint.route("/", methods=["GET", "POST"])
def list_route():
    form_create = forms.OrchardCreateForm()
    if form_create.validate_on_submit():
        name = form_create.name.data
        db.db.session.add(db.Orchard(name=name))
        db.db.session.commit()
        return redirect(url_for("orchard.list_route"))
    return render_template(
        "orchard/list.html",
        orchards=db.db.session.execute(
            db.db.select(db.Orchard)
        ).scalars(),
        form_create=form_create,
    )


@blueprint.route("/<int:pk>/", methods=["GET", "POST"])
def detail_route(pk):
    orchard = db.db.get_or_404(db.Orchard, pk)
    form = forms.OrchardUpdateForm(data={
        "name": orchard.name,
    })
    if "_update" in request.form and form.validate_on_submit():
        orchard.name = form.name.data

        db.db.session.commit()
        return redirect(url_for("orchard.detail_route", pk=pk))

    """
    form_override_excel = forms.OrchardOverrideFromExcel(prefix="excel")
    if "_override_excel" in request.form and form_override_excel.validate_on_submit():
        orchard.override_from_excel(
            f=io.BytesIO(request.files["excel-file"].read()),
            distance_between_trees=form_override_excel.distance_between_trees.data,
            distance_from_trees=form_override_excel.distance_from_trees.data,
        )
        db.db.session.commit()
        return redirect(url_for("orchard.detail_route", pk=pk))
    """

    return render_template(
        "orchard/detail.html",
        orchard=orchard,
        form=form,
        form_import_points=forms.OrchardImportPoints(),
    )


@blueprint.route("/<int:pk>/jalons/", methods=["GET", "POST"])
def import_points_route(pk):
    if request.method == "GET":
        return redirect(url_for("orchard.detail_route", pk=pk))

    orchard = db.db.get_or_404(db.Orchard, pk)

    form_save = forms.OrchardOverrideFromPoints()
    if "_save" in request.form and form_save.validate_on_submit():
        print("todo")
        db.db.session.commit()
        return redirect(url_for("orchard.detail_route", pk=pk))

    form = forms.OrchardImportPoints()
    if not form.validate_on_submit():
        flash_error(form.errors)
        return redirect(url_for("orchard.detail_route", pk=pk))

    wb = load_workbook(io.BytesIO(request.files["file"].read()))
    ws = wb["Jalons"]
    latlngs = [
        [row[5], row[6]]
        for i, row in enumerate(ws.values)
        if i > 0
    ]

    return render_template(
        "orchard/import_points.html",
        orchard=orchard,
        form_save=form_save,
        latlngs=latlngs,
    )
