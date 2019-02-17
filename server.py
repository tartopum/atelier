import argparse
import locale
import logging
import logging.config
import os

from gevent.pywsgi import WSGIServer

from atelier.debug import CONTROLLINO_LOG_PATH

try:
    locale.setlocale(locale.LC_ALL, ("fr_FR", "UTF-8"))
except locale.Error:
    pass

HERE = os.path.dirname(__file__)
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.config.dictConfig(dict(
    version = 1,
    formatters = {
        "message": {
            "format": "%(message)s"
        },
        "date": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
        }
    },
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "message",
            "level": logging.INFO,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(HERE, "logs.txt"),
            "formatter": "date",
            "level": logging.WARNING,
            "maxBytes": 50000,
            "backupCount": 3,

        },
        "file_debug": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": CONTROLLINO_LOG_PATH,
            "formatter": "message",
            "level": logging.DEBUG,
            "maxBytes": 10000000,
        },
    },
    root = {
        "handlers": ["file", "console"],
        "level": logging.DEBUG,
    },
    loggers = {
        "scheduler": {
            "handlers": ["file", "console"],
            "level": logging.WARNING,
        },
        "debug": {
            "handlers": ["file_debug"],
            "level": logging.DEBUG,
        },
        "flask.app": {
            "handlers": ["file", "console"],
            "level": logging.WARNING,
        },
    },
))

from atelier import app, db, config, config_arduino, scheduler


def remove_console_logging(logger):
    for handler in logger.handlers:
        if handler.name == "console":
            logger.handlers.remove(handler)
            return


def run_server():
    app.debug = config["server"]["debug"]
    if app.debug:
        app.logger.setLevel(logging.INFO)
    else:
        remove_console_logging(scheduler.logger)
        remove_console_logging(app.logger)
    http_server = WSGIServer(("", config["server"]["port"]), app)
    http_server.serve_forever()


if __name__ == "__main__":
    db.create_tables()
    config_arduino()
    scheduler.run()
    run_server()
