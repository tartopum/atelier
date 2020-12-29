import os
import argparse
import locale
import logging
import logging.config
import subprocess as sp

from gevent.pywsgi import WSGIServer
import requests

from server.monitoring import CONTROLLINO_LOG_PATH, ATELIER_LOG_PATH

try:
    locale.setlocale(locale.LC_ALL, ("fr_FR", "UTF-8"))
except locale.Error:
    pass

HERE = os.path.dirname(__file__)
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.config.dictConfig(
    dict(
        version=1,
        formatters={
            "message": {"format": "%(message)s"},
            "date": {
                "format": "[%(asctime)s][%(name)-12s][%(levelname)-8s] %(message)s"
            },
        },
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "message",
                "level": logging.DEBUG,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": ATELIER_LOG_PATH,
                "formatter": "date",
                "level": logging.INFO,
                "maxBytes": 1000000,
                "backupCount": 3,
            },
            "file_debug": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": CONTROLLINO_LOG_PATH,
                "formatter": "message",
                "level": logging.DEBUG,
                "maxBytes": 5000000,
                "backupCount": 1,  # If zero, rollover never occurs
            },
        },
        root={"handlers": ["file", "console"], "level": logging.DEBUG},
        loggers={
            "scheduler": {"handlers": ["file", "console"], "level": logging.WARNING},
            "debug": {"handlers": ["file_debug"], "level": logging.DEBUG},
            "atelier": {"handlers": ["file", "console"], "level": logging.DEBUG},
        },
    )
)

from server import alerts, arduino, db, scheduler, web
from server.config import config


logger = logging.getLogger("atelier")


def remove_logging_handler(logger, handler_name):
    for handler in logger.handlers:
        if handler.name == handler_name:
            logger.handlers.remove(handler)
            return


def run_dev_server():
    web.app.logger.setLevel(logging.DEBUG)
    env = {**os.environ, "FLASK_APP": "server.web", "FLASK_ENV": "development"}
    sp.run(["poetry", "run", "flask", "run"], check=True, env=env)


def run_prod_server():
    web.app.debug = False
    web.app.logger.setLevel(logging.INFO)
    http_server = WSGIServer(("", config["server"]["port"]), web.app)
    http_server.serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if not args.debug:
        remove_logging_handler(web.app.logger, "console")
        remove_logging_handler(scheduler.logger, "console")

    db.create_tables()

    try:
        arduino.configure()
    except requests.exceptions.RequestException as e:
        logger.error(str(e), exc_info=e)

    scheduler.run(min(10, config["server"]["debug_period"]))

    alerts.raise_alert(
        "startup",
        "La Raspberry a redémarré, il semble y avoir eu une coupure de courant.",
        0,
    )

    if args.debug:
        run_dev_server()
    else:
        run_prod_server()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(str(e), exc_info=e)
        raise e
