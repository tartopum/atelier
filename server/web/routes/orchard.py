from flask import Blueprint, render_template, redirect, url_for

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


@blueprint.route("/<int:id>/")
def detail_route(id):
    return render_template(
        "orchard/detail.html",
        orchard=db.db.get_or_404(db.Orchard, id),
    )
