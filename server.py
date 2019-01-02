import argparse
import logging
import logging.config
import os

from gevent.pywsgi import WSGIServer

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
            "maxBytes": 50000,
            "backupCount": 3

        },
    },
    root = {
        "handlers": ["file"],
        "level": logging.DEBUG,
    },
    loggers = {
        "scheduler": {
            "handlers": ["file"],
            "level": logging.WARNING,
        }
    },
))

from atelier import app, db, config, config_arduino, scheduler


def run_server():
    app.debug = config["server"]["debug"]
    http_server = WSGIServer(("", config["server"]["port"]), app)
    http_server.serve_forever()


if __name__ == "__main__":
    db.create_tables()
    config_arduino()
    scheduler.run()
    run_server()
