import csv
import io
import json
import math

from flask import Blueprint, render_template, redirect, url_for, request
from haversine import haversine, inverse_haversine
from shapely.geometry import MultiPoint

from .base import flash_error
from ... import db
from .. import forms

blueprint = Blueprint("orchard", __name__)


@blueprint.route("/", methods=["GET", "POST"])
def list_route():
    form_create = forms.OrchardCreateForm()
    if form_create.validate_on_submit():
        name = form_create.name.data
        orchard = db.Orchard(name=name)
        db.db.session.add(orchard)
        db.db.session.commit()
        return redirect(url_for("orchard.detail_route", pk=orchard.id))
    return render_template(
        "orchard/list.html",
        orchards=db.db.session.execute(
            db.db.select(db.Orchard).order_by(db.Orchard.name)
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

    return render_template(
        "orchard/detail.html",
        orchard=orchard,
        rows_json=json.dumps(orchard.rows) if orchard.rows else None,
        form=form,
        form_import_points=forms.OrchardImportPoints(),
    )


def compute_azimuth(p1, p2):
  lat1, lon1 = p1
  lat2, lon2 = p2
  lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
  dLon = lon2 - lon1

  x = math.sin(dLon) * math.cos(lat2)
  y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)

  bearing = math.atan2(x, y)
  bearing = math.degrees(bearing)

  return (bearing + 360) % 360  # Azimut entre 0 et 360°


@blueprint.route("/<int:pk>/jalons/", methods=["GET", "POST"])
def import_points_route(pk):
    if request.method == "GET":
        return redirect(url_for("orchard.detail_route", pk=pk))

    orchard = db.db.get_or_404(db.Orchard, pk)

    form_save = forms.OrchardOverrideFromPoints()
    if "_save" in request.form and form_save.validate_on_submit():
        orchard.rows = []
        mapped_points = []
        for p1, p2 in json.loads(form_save.mapping.data).items():
            if not p2 or p1 in mapped_points or p2 in mapped_points:
                continue

            start = list(map(float, p1.split(",")))
            end = list(map(float, p2.split(",")))

            # La mesure n'a pas été prise au niveau du tronc exactement mais
            # à une certaine distance de celui-ci. On calcule sa position
            bearing = math.radians(compute_azimuth(start, end))
            start = inverse_haversine(start, form_save.distance_from_trees.data / 1000, bearing)
            end = inverse_haversine(end, form_save.distance_from_trees.data / 1000, bearing + math.pi)

            length = haversine(start, end) * 1000  # km -> m
            n_trees = math.ceil(length / form_save.distance_between_trees.data)
            distance_between_trees = length / n_trees
            orchard.rows.append({
                "length": length,
                "bearing": bearing,
                "distance_between_trees_theoretical": form_save.distance_between_trees.data,
                "distance_between_trees": distance_between_trees,
                "trees": [
                    start,
                    *[
                        inverse_haversine(start, (i+1) * distance_between_trees / 1000, bearing)
                        for i in range(n_trees - 1)
                    ],
                    end,
                ],
            })
            mapped_points.append(p1)
            mapped_points.append(p2)

        points = [
            tree
            for row in orchard.rows
            for tree in row["trees"]
        ]
        centroid = MultiPoint([
            (lng, lat)
            for lat, lng in points
        ]).centroid
        orchard.lng = centroid.x
        orchard.lat = centroid.y

        db.db.session.commit()
        return redirect(url_for("orchard.detail_route", pk=pk))

    form = forms.OrchardImportPoints()
    if not form.validate_on_submit():
        flash_error(form.errors)
        return redirect(url_for("orchard.detail_route", pk=pk))

    reader = csv.reader(io.StringIO(request.files["file"].read().decode("utf-8")))
    latlngs = [
        [float(lat), float(lng)]
        for lat, lng in reader
    ]

    return render_template(
        "orchard/import_points.html",
        orchard=orchard,
        form_save=form_save,
        latlngs=latlngs,
    )


@blueprint.route("/<int:pk>/carte-preco/creer/", methods=["GET", "POST"])
def recommendation_map_create_route(pk):
    orchard = db.db.get_or_404(db.Orchard, pk)
    form = forms.RecommendationMapCreateForm()
    if form.validate_on_submit():
        choices = [
            getattr(form, f"choice{i+1}").data
            for i in range(5)
            if getattr(form, f"choice{i+1}").data
        ]
        map_ = db.RecommendationMap(
            orchard_id=orchard.id,
            title=form.title.data,
            choices={
                c: {"color": db.RecommendationMap.COLORS[i]} for i, c in enumerate(choices)
            },
            observations=[
                [None for tree in row["trees"]]
                for row in orchard.rows
            ],
        )
        db.db.session.add(map_)
        db.db.session.commit()
        return redirect(url_for("orchard.recommendation_map_route", orchard_id=orchard.id, pk=map_.id))

    return render_template(
        "orchard/recommendation_map_create.html",
        orchard=orchard,
        form=form,
    )


@blueprint.route("/<int:orchard_id>/carte-preco/<int:pk>/", methods=["GET", "POST"])
def recommendation_map_route(orchard_id, pk):
    map_ = db.db.get_or_404(db.RecommendationMap, pk)
    return render_template(
        "orchard/recommendation_map.html",
        orchard=map_.orchard,
        map_=map_,
    )
