from flask_wtf import FlaskForm
import jsonschema
from wtforms import Form, FieldList, FormField, FileField, FloatField, HiddenField, IntegerField, StringField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from wtforms.widgets import NumberInput, TextArea

from .. import config


def _make_parameter_validator(parameter):
    def validate(form, field):
        if field.data is None:  # Didn't pass previous checks
            return
        try:
            jsonschema.validate(field.data, parameter)
        except jsonschema.ValidationError as e:
            raise ValidationError(str(e))

    return validate


def _parameter_to_field(name, parameter):
    if parameter["type"] == "string":
        field_cls = StringField
    if parameter["type"] == "integer":
        field_cls = IntegerField
    if parameter["type"] == "number":
        field_cls = FloatField
    return field_cls(
        parameter.get("title") or name,
        [InputRequired(), _make_parameter_validator(parameter)],
        description=parameter.get("description", ""),
    )


def _from_schema_section(section):
    class SectionForm(Form):
        pass

    for name, parameter in config.schema["properties"][section]["properties"].items():
        setattr(SectionForm, name, _parameter_to_field(name, parameter))
    return SectionForm


_config_form_cls = {
    section: _from_schema_section(section) for section in config.editable_sections
}


class ConfigForms(dict):
    def __init__(self, data=None):
        for section, form in _config_form_cls.items():
            title = config.schema["properties"][section]["title"]
            self[section] = (
                title or section,
                form(data, **config.get(section), prefix=section),
            )

    def validate(self):
        return all(form.validate() for _, form in self.values())

    def populate_config(self):
        if not self.validate():
            raise ValueError("The forms must be validated.")
        for section, (_, form) in self.items():
            for field in form:
                config.set(section, field.short_name, field.data)
        config.validate()


class OrchardCreateForm(FlaskForm):
    name = StringField("Ajouter un verger :")


class OrchardRowForm(FlaskForm):
    lat_start = FloatField(validators=[InputRequired()])
    lng_start = FloatField(validators=[InputRequired()])
    lat_stop = FloatField(validators=[InputRequired()])
    lng_stop = FloatField(validators=[InputRequired()])
    n_trees = IntegerField(validators=[InputRequired()])


class OrchardUpdateForm(FlaskForm):
    name = StringField("Nom :")
    rows = FieldList(FormField(OrchardRowForm), min_entries=0)


class OrchardImportPoints(FlaskForm):
    file = FileField("", validators=[InputRequired()])


class OrchardOverrideFromPoints(FlaskForm):
    mapping = HiddenField(validators=[InputRequired()])
    distance_from_trees = FloatField(
        "Distance entre la mesure et le tronc (m) :",
        validators=[InputRequired()],
        widget=NumberInput(step=0.1),
    )
    distance_between_trees = FloatField(
        "Distance entre deux arbres du même rang (m) :",
        validators=[InputRequired()],
        default=2,
        widget=NumberInput(step=0.1),
    )
