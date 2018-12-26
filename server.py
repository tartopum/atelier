import argparse
import logging
import logging.config
import os

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
            "level": logging.WARNING
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(HERE, "logs.txt"),
            "formatter": "date",
            "level": logging.WARNING,
            "maxBytes": 1024,
            "backupCount": 3

        },
    },
    root = {
        "handlers": ["console"],
        "level": logging.DEBUG,
    },
    loggers = {
        "scheduler": {
            "handlers": ["file"],
            "level": logging.WARNING,
        }
    },
))

from atelier import app, config, scheduler


def run_server():
    #app.debug = True # TODO
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    config.from_cmdline()
    scheduler.run()
    run_server()
