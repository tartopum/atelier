import argparse
from collections import defaultdict
import copy
import json
import os

import jsonschema

_HERE = os.path.dirname(__file__)
_PATH = os.path.join(_HERE, "..", "config.json")


class Schema(dict):
    def __init__(self):
        self["type"] = "object"
        self["additionalProperties"] = False
        self["properties"] = {}

    def add_section(self, name, title="", required=True):
        if required:
            if "required" not in self:
                self["required"] = []
            self["required"].append(name)
        self["properties"][name] = {
            "type": "object",
            "title": title,
            "additionalProperties": False,
            "required": [],
            "properties": {}
        }

    def add_parameter(self, section, name, schema, title="", required=True):
        if section not in self["properties"]:
            self.add_section(section)
        schema = {**schema, "title": title}
        self["properties"][section]["required"].append(name)
        self["properties"][section]["properties"][name] = schema

    def add_ip(self, section, parameter, **kwargs):
        self.add_parameter(
            section,
            parameter,
            {"type": "string", "format": "ipv4"},
            **kwargs
        )

    def add_int(self, section, parameter, min=None, max=None, **kwargs):
        schema = {"type": "integer"}
        if min is not None:
            schema["minimum"] = min
        if max is not None:
            schema["maximum"] = max
        self.add_parameter(section, parameter, schema, **kwargs)

    def add_port(self, section, parameter, **kwargs):
        self.add_int(section, parameter, min=0, max=65535, **kwargs)

    def add_period(self, section, **kwargs):
        self.add_section(section, **kwargs)
        parameter_schema = {
            "type": "string",
            "pattern": "^[0-9]{2}:[0-9]{2}$"
        }
        self.add_parameter(section, "beginning", parameter_schema, title="Début")
        self.add_parameter(section, "end", parameter_schema, title="Fin")


class Config(dict):
    READONLY_KEYS = ["server", "arduino"]

    def __init__(self, schema, path):
        self.schema = schema
        self.path = path
        self._persistent = {}
        self.load(path)

    def _read_cmdline(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", type=int, help="Server HTTP port")
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--aip", help="Arduino IP address")
        parser.add_argument("--aport", type=int, help="Arduino HTTP port")
        args = parser.parse_args()

        self["server"]["debug"] = int(args.debug)
        if args.port is not None:
            self["server"]["port"] = args.port

        if args.aip is not None:
            self["arduino"]["ip"] = args.aip
        if args.aport is not None:
            self["arduino"]["port"] = args.aport

    @property
    def editable(self):
        return {k: v for k, v in self.items() if k not in self.READONLY_KEYS}

    def _clear(self):
        for k in self:
            del self[k]

    def _fill(self):
        self._clear()
        for k, v in self._persistent.items():
            self[k] = dict(v)  # Copy dict
        self._read_cmdline()

    def load(self, path):
        self.path = path
        with open(self.path) as f:
            self._persistent = json.load(f)
        self._fill()
        self.validate()

    def validate(self):
        jsonschema.validate(self, self.schema, format_checker=jsonschema.FormatChecker())

    def save(self):
        self.validate()
        for k, v in self.items():
            if k in self.READONLY_KEYS:
                continue
            self._persistent[k] = dict(v)
        with open(self.path, "w") as f:
            json.dump(self._persistent, f, indent=2)


schema = Schema()

schema.add_section("server", "Serveur")
schema.add_ip("server", "ip")
schema.add_port("server", "port")
schema.add_parameter("server", "db_path", {"type": "string"})
schema.add_parameter("server", "credentials", {
    "type": "array",
    "minItems": 2,
    "maxItems": 2,
    "items": {
        "type": "string"
    }
})
schema.add_int("server", "debug", min=0, max=1)
schema.add_int("server", "max_alert_day_old", min=1, max=365) # days

schema.add_section("arduino", "Arduino")
schema.add_ip("arduino", "ip")
schema.add_port("arduino", "port")
schema.add_int("arduino", "timeout", min=1, max=10)  # s

schema.add_period("lunch_period", title="Période de midi")
schema.add_period("sleep_period", title="Période de nuit")

schema.add_section("alarm", "Alarme")
schema.add_int("alarm", "delay", min=0, max=60, title="Délai de déclenchement (s)")  # s

schema.add_section("lights", "Lumières")
schema.add_int("lights", "press_delay", min=1, max=10, title="Durée de pression des boutons (s)")  # s
schema.add_int("lights", "inactivity_delay", min=1, max=60, title="Délai d'inactivité (min)")  # min

schema.add_section("tank", "Eau")
schema.add_int("tank", "flow_check_period", min=5, max=120, title="Durée entre deux calculs de débit (s)")  # s
schema.add_int("tank", "min_flow_in", min=0, max=100, title="Débit minimal de la pompe du puits (L/min)")  # L/min
schema.add_int("tank", "time_to_fill_up", min=1, max=(60 * 24), title="Durée entre deux remplissages (min)")  # min
schema.add_int("tank", "volume_before_pump_out", min=1, max=10000, title="Volume dans la cuve avant d'éteindre la ville (L)")  # L
schema.add_int("tank", "filter_cleaning_period", min=1, max=(60 * 24 * 7), title="Durée entre deux nettoyages du filtre (min)")  # min
schema.add_int("tank", "filter_cleaning_duration", min=1, max=30, title="Durée d'ouverture du filtre (s)")  # s
schema.add_int("tank", "pump_in_start_duration", min=1, max=300, title="Temps mis par l'eau pour remonter le puits (s)")  # s
schema.add_int("tank", "max_pump_out_running_time", min=1, max=60, title="Durée maximale de fonctionnement de la pompe du surpresseur (min)")  # min
schema.add_int("tank", "height_between_sensors", min=1, max=1000, title="Distance entre les capteurs de niveau de la cuve (cm)")  # cm
schema.add_int("tank", "radius", min=1, max=1000, title="Rayon de la cuve (cm)")  # cm

config = Config(schema, _PATH)
