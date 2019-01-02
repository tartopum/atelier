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


class ArduinoConnectionJob:
    REMINDER_DELAY = 15 * 60

    def __init__(self):
        self.alert_raised = False
        self.last_raise_time = None
    
    def _can_raise(self):
        return (
            not self.alert_raised or
            time.time() - self.last_raise_time > self.REMINDER_DELAY
        )

    def _run_job_safely(self, f):
        try:
            f()
        except requests.exceptions.RequestException as e:
            if not self._can_raise():
                return
            self.alert_raised = True
            self.last_raise_time = time.time()

            logger.error(e)
            raise_alert(
                "arduino_connection_error",
                "La Controllino est injoignable."
            )
        else:
            self.alert_raised = False


class PeriodJob(ArduinoConnectionJob, metaclass=abc.ABCMeta):
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

    def _safe_beginning(self):
        self._run_job_safely(self.beginning)

    def _safe_end(self):
        self._run_job_safely(self.end)

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


class TankJob(ArduinoConnectionJob):
    def __init__(self, every):
        self._every = None
        self.every = every

    @property
    def every(self):
        self._every

    @every.setter
    def every(self, val):
        self._every = val
        schedule.cancel_job(self.job)
        schedule.every(self._every).seconds.do(self.job)

    def _unsafe_job(self):
        state = arduino.read_state(tank)
        db.add_tank_state(state)

    def job(self):
        self._run_job_safely(self._unsafe_job)


lunch_job = LunchJob(
    config["lunch_period"]["beginning"],
    config["lunch_period"]["end"]
)
sleep_job = SleepJob(
    config["sleep_period"]["beginning"],
    config["sleep_period"]["end"]
)

tank_job = TankJob(config["tank"]["flow_check_period"])
