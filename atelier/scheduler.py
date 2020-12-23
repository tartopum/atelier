import abc
import logging
import threading
import time
import traceback
import sys
from uuid import uuid4

import requests
from requests.exceptions import ConnectionError, ReadTimeout
import schedule

from .config import config
from .helpers import raise_alert, ALERT_LEVEL_SMS
from . import alarm, arduino, db, fence, lights, tank, workshop
from .debug import get_controllino_log

logger = logging.getLogger("atelier")
debug_logger = logging.getLogger("debug")


class ScheduleThread(threading.Thread):
    def __init__(self, interval, stop_event):
        super().__init__()
        self.interval = interval
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(e)
            time.sleep(self.interval)


def run(interval):
    # https://schedule.readthedocs.io/en/stable/faq.html#how-to-continuously-run-the-scheduler-without-blocking-the-main-thread
    cease_continuous_run = threading.Event()
    continuous_thread = ScheduleThread(interval, cease_continuous_run)
    continuous_thread.start()
    return cease_continuous_run


class Job:
    def __init__(self):
        self._id = str(uuid4())

    def clear(self):
        schedule.clear(self._id)


class ArduinoConnectionJob(Job):
    REMINDER_DELAY = 15 * 60

    def __init__(self):
        super().__init__()
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
                "La Controllino est injoignable.",
                level=ALERT_LEVEL_SMS
            )
        else:
            self.alert_raised = False


class PeriodJob(ArduinoConnectionJob, metaclass=abc.ABCMeta):
    def __init__(self, btime, etime):
        super().__init__()
        self._time_range = None
        self.time_range = (btime, etime)

    @property
    def time_range(self):
        return self._time_range

    @time_range.setter
    def time_range(self, range_):
        btime, etime = range_
        schedule.clear(self._id)
        schedule.every().day.at(btime).do(self._safe_beginning).tag(self._id)
        schedule.every().day.at(etime).do(self._safe_end).tag(self._id)

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


class SafeJob(ArduinoConnectionJob, metaclass=abc.ABCMeta):
    def __init__(self, unsafe_job):
        super().__init__()
        self.unsafe_job = unsafe_job

    def job(self):
        self._run_job_safely(self.unsafe_job)


class EveryJob(SafeJob, metaclass=abc.ABCMeta):
    def __init__(self, unit, every, unsafe_job):
        super().__init__(unsafe_job)
        self.unit = unit
        self._every = None
        self.every = every

    @property
    def every(self):
        return self._every
    
    @every.setter
    def every(self, val):
        self._every = val
        self.clear()
        if self.every is not None:
            getattr(schedule.every(self.every), self.unit).do(self.job).tag(self._id)


class DayJob(SafeJob, metaclass=abc.ABCMeta):
    def __init__(self, at, unsafe_job):
        super().__init__(unsafe_job)
        self._at = None
        self.at = at

    @property
    def at(self):
        return self._at
    
    @at.setter
    def at(self, val):
        self._at = val
        self.clear()
        if self.at is not None:
            schedule.every().day.at(self.at).do(self.job).tag(self._id)


def start_alarm():
    alarm.listen(1)


tank_job = EveryJob(
    "seconds",
    config["tank"]["stats_collection_period"],
    tank.read_and_store_stats
)
lunch_job = DayJob(config["alarm"]["lunch"], start_alarm)
night_job = DayJob(config["alarm"]["night"], start_alarm)

schedule.every().day.at("00:00").do(db.delete_old_alerts)
schedule.every().day.at("00:05").do(db.backup)

def debug():
    debug_logger.debug(get_controllino_log())

debug_job = EveryJob("seconds", None, debug)
