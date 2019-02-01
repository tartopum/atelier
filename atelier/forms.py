import jsonschema
from wtforms import Form, FloatField, IntegerField, StringField
from wtforms.validators import InputRequired, ValidationError

from .config import config, schema


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
        [InputRequired(), _make_parameter_validator(parameter)]
    )


def _from_schema_section(section): 
    class SectionForm(Form): pass
    for name, parameter in schema["properties"][section]["properties"].items():
        setattr(SectionForm, name, _parameter_to_field(name, parameter))
    return SectionForm


_config_form_cls = {
    section: _from_schema_section(section)
    for section in config.editable
}


class ConfigForms(dict):
    def __init__(self, data=None):
        for section, form in _config_form_cls.items():
            title = schema["properties"][section]["title"]
            self[section] = (
                title or section,
                form(data, **config[section], prefix=section)
            )

    def validate(self):
        return all(form.validate() for _, form in self.values())

    def populate_config(self):
        if not self.validate():
            raise ValueError("The forms must be validated.")
        for section, (_, form) in self.items():
            for field in form:
                config[section][field.short_name] = field.data
        config.validate()
