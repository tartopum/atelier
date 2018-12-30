import abc
import logging
import threading
import time
import traceback
import sys

import requests
from requests.exceptions import ConnectionError, ReadTimeout
import schedule

from .config import config
from .helpers import raise_alert
from . import alarm, arduino, db, lights, tank, workshop

logger = logging.getLogger("scheduler")


class ScheduleThread(threading.Thread):
    def __init__(self, interval, stop_event):
        super().__init__()
        self.interval = interval
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(self.interval)


def run(interval=10):
    # https://schedule.readthedocs.io/en/stable/faq.html#how-to-continuously-run-the-scheduler-without-blocking-the-main-thread
    cease_continuous_run = threading.Event()
    continuous_thread = ScheduleThread(interval, cease_continuous_run)
    continuous_thread.start()
    return cease_continuous_run


class PeriodJob(abc.ABC):
    def __init__(self, btime, etime):
        self._time_range = None
        self.time_range = (btime, etime)

    @property
    def time_range(self):
        return self._time_range

    @time_range.setter
    def time_range(self, range_):
        btime, etime = range_
        schedule.cancel_job(self._safe_beginning)
        schedule.cancel_job(self._safe_end)
        schedule.every().day.at(btime).do(self._safe_beginning)
        schedule.every().day.at(etime).do(self._safe_end)

    def _make_job_safe(self, f):
        try:
            f()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            raise_alert(
                "arduino_connection_error",
                "La Controllino est injoignable."
            )

    def _safe_beginning(self):
        self._make_job_safe(self.beginning)

    def _safe_end(self):
        self._make_job_safe(self.end)

    @abc.abstractmethod
    def beginning(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def end(self):
        raise NotImplementedError()


class LunchJob(PeriodJob):
    def beginning(self):
        alarm.listen(1)

    def end(self):
        alarm.listen(0)


class SleepJob(PeriodJob):
    def beginning(self):
        alarm.listen(1)
        workshop.power_supply(0)
        lights.activate_all(0)

    def end(self):
        alarm.listen(0)
        workshop.power_supply(1)


def read_tank_state():
    try:
        state = arduino.read_state(tank)
    except (ConnectionError, ReadTimeout) as e:
        logger.error(e)
        raise_alert(
            "arduino_connection_error",
            "Impossible de récupérer l'état de la cuve."
        )
    else:
        db.add_tank_state(state)


lunch_job = LunchJob(
    config["lunch_period"]["beginning"],
    config["lunch_period"]["end"]
)
sleep_job = SleepJob(
    config["sleep_period"]["beginning"],
    config["sleep_period"]["end"]
)
schedule.every(config["tank"]["read_state_period"]).seconds.do(read_tank_state)
