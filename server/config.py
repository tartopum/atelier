import os
import json

import jsonschema


class NotValidatedError(ValueError):
    pass


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
            "properties": {},
        }

    def add_parameter(self, section, name, schema, title="", description="", required=True):
        if section not in self["properties"]:
            self.add_section(section)
        schema = {**schema, "title": title, "description": description}
        self["properties"][section]["required"].append(name)
        self["properties"][section]["properties"][name] = schema

    def add_ip(self, section, parameter, **kwargs):
        self.add_parameter(
            section, parameter, {"type": "string", "format": "ipv4"}, **kwargs
        )

    def add_number(
        self, section, parameter, min=None, max=None, type="number", **kwargs
    ):
        schema = {"type": type}
        if min is not None:
            schema["minimum"] = min
        if max is not None:
            schema["maximum"] = max
        self.add_parameter(section, parameter, schema, **kwargs)

    def add_int(self, *args, **kwargs):
        self.add_number(*args, type="integer", **kwargs)

    def add_port(self, section, parameter, **kwargs):
        self.add_int(section, parameter, min=0, max=65535, **kwargs)

    def add_time(self, section, parameter, **kwargs):
        schema = {"type": "string", "pattern": "^[0-9]{2}:[0-9]{2}$"}
        self.add_parameter(section, parameter, schema, **kwargs)

    def add_period(self, section, **kwargs):
        self.add_time(section, "beginning", title="Début")
        self.add_time(section, "end", title="Fin")


schema = Schema()

schema.add_section("server", "Serveur")
schema.add_ip("server", "ip")
schema.add_port("server", "port")
schema.add_parameter("server", "secret_key", {"type": "string", "minLength": 50})
schema.add_parameter("server", "db_path", {"type": "string", "minLength": 1})
schema.add_parameter(
    "server", "db_backup_paths", {"type": "array", "items": {"type": "string"}}
)
schema.add_parameter(
    "server",
    "http_credentials",
    {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "string"}},
)
schema.add_parameter(
    "server",
    "sms_credentials",
    {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "string"}},
)
schema.add_int("server", "debug", min=0, max=1)
schema.add_int("server", "debug_period", min=1, max=86400)
schema.add_int("server", "max_alert_day_old", min=1, max=365)

schema.add_section("arduino", "Arduino")
schema.add_ip("arduino", "ip")
schema.add_port("arduino", "port")
schema.add_int("arduino", "timeout", min=1, max=10)

schema.add_section("power", "Alimentation")
schema.add_int(
    "power",
    "delay_before_reminder",
    min=1,
    max=500,
    title="Délai en mode manuel avant rappel (h)",
)

schema.add_section("alarm", "Alarme")
schema.add_int(
    "alarm", "delay_before_alert", min=0, max=60, title="Délai avant déclenchement (s)", description="Si une présence est détectée, on attend un peu avant de déclencher l'alarme pour éviter les faux positifs.",
)
schema.add_int(
    "alarm",
    "delay_before_listening",
    min=0,
    max=60,
    title="Délai avant mise en écoute (s)",
    description="Au démarrage de la carte, le détecteur de mouvement est activé. On attend un peu qu'il s'éteigne sinon on déclencherait l'alarme.",
)
schema.add_time("alarm", "lunch", title="Midi")
schema.add_time("alarm", "night", title="Nuit")

schema.add_section("lights", "Lumières")
schema.add_number(
    "lights", "press_delay", min=0.1, max=5, title="Durée de pression des boutons (s)"
)
schema.add_int(
    "lights", "inactivity_delay", min=1, max=60, title="Délai d'inactivité (min)", description="Si aucune présence est détectée durant cette période, les lumières intérieures sont éteintes."
)

schema.add_section("tank", "Eau")
schema.add_int(
    "tank",
    "stats_collection_period",
    min=10,
    max=3600,
    title="Fréquence de collection des statistiques (s)",
)
schema.add_int(
    "tank",
    "flow_check_period",
    min=5,
    max=120,
    title="Durée entre deux calculs de débit (s)",
)
schema.add_int(
    "tank",
    "min_flow_in",
    min=0,
    max=100,
    title="Débit minimal de la pompe du puits (L/min)",
    description="En-dessous de ce débit, on arrête la pompe du puits et attend que ce dernier se re-remplisse.",
)
schema.add_int(
    "tank",
    "time_to_fill_up",
    min=1,
    max=(60 * 24),
    title="Durée entre deux remplissages (min)",
    description="Durée estimée de remplissage du puits, c'est-à-dire entre deux allumages de la pompe du puits.",
)
schema.add_int(
    "tank",
    "volume_before_pump_out",
    min=1,
    max=10000,
    title="Volume dans la cuve avant d'éteindre la ville (L)",
    description="Pour éviter d'éteindre la ville et de la rallumer immédiatement, on s'assure que la cuve est un minimum pleine avant de basculer dessus.",
)
schema.add_int(
    "tank",
    "filter_cleaning_period",
    min=1,
    max=(60 * 24 * 7),
    title="Durée entre deux nettoyages du filtre (min)",
)
schema.add_int(
    "tank",
    "filter_cleaning_duration",
    min=1,
    max=30,
    title="Durée d'ouverture du filtre (s)",
)
schema.add_int(
    "tank",
    "filter_cleaning_consecutive_delay",
    min=1,
    max=60,
    title="Durée entre deux ouvertures consécutives du filtre (s)",
    description="Pour bien le décrasser, on ouvre le filtre deux fois à chaque nettoyage.",
)
schema.add_int(
    "tank",
    "pump_in_start_duration",
    min=1,
    max=300,
    title="Temps mis par l'eau pour remonter le puits (s)",
    description="Si à l'allumage de la pompe du puits on n'a pas de débit pendant cette durée, on considère que c'est normal.",
)
schema.add_int(
    "tank",
    "max_pump_out_running_time",
    min=1,
    max=60,
    title="Durée maximale de fonctionnement de la pompe du surpresseur (min)",
)
schema.add_int(
    "tank",
    "min_pump_out_stop_time",
    min=1,
    max=60,
    title="Durée minimale de pause de la pompe du surpresseur (min)",
    description="Quand la membrane du surpresseur est détendue, le capteur de pression commandant la pompe du surpresseur n'est pas fiable et peut mener à des démarrages/arrêts à fréquence rapide de la pompe. Quand cela arrive, il faut une action manuelle pour regonfler la membrane.",
)
schema.add_int(
    "tank",
    "max_duration_without_flow_out",
    min=1,
    max=120,
    title="Durée maximale sans consommation détectée (min)",
    description="Si aucune consommation est détectée pendant cette période, on lève une alerte car cela peut signifier qu'il y a un problème de sortie d'eau.",
)
schema.add_int(
    "tank",
    "height_between_sensors",
    min=1,
    max=1000,
    title="Distance entre les capteurs de niveau de la cuve (cm)",
)
schema.add_int("tank", "radius", min=1, max=1000, title="Rayon de la cuve (cm)")
schema.add_int(
    "tank",
    "low_sensor_height",
    min=1,
    max=1000,
    title="Hauteur du capteur de niveau bas (cm)",
)
schema.add_int(
    "tank", "pump_in_power", min=1, max=5000, title="Puissance de la pompe de puits (W)"
)
schema.add_int(
    "tank",
    "pump_out_power",
    min=1,
    max=5000,
    title="Puissance de la pompe du surpresseur (W)",
    description="Pour calculer la consommation électrique.",
)
schema.add_int(
    "tank",
    "urban_network_power",
    min=1,
    max=1000,
    title="Puissance de l'électrovanne de ville (W)",
    description="Pour calculer la consommation électrique.",
)

_config = {}
_validated = False
_READONLY_SECTIONS = ["server", "arduino"]

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
CONTROLLINO_LOG_PATH = os.path.join(BASE_DIR, "controllino.log")
ATELIER_LOG_PATH = os.path.join(BASE_DIR, "atelier.log")
SCHEDULER_LOG_PATH = os.path.join(BASE_DIR, "scheduler.log")


editable_sections = [k for k in schema["properties"] if k not in _READONLY_SECTIONS]


def load(path=CONFIG_PATH):
    global _config, _validated
    with open(path) as f:
        _config = json.load(f)
    _validated = False


def validate():
    global _validated
    jsonschema.validate(_config, schema, format_checker=jsonschema.FormatChecker())
    _validated = True


def get(section, field=None):
    global _validated
    if not _validated:
        raise NotValidatedError()
    val = _config[section]
    if field is None:
        return val
    return val[field]


def set(section, field, val):
    if section in _READONLY_SECTIONS:
        raise ValueError(f"Section '{section}' is readonly.")
    _config[section][field] = val


def save(path=CONFIG_PATH):
    with open(path, "w") as f:
        json.dump(_config, f, indent=2)


load()
