import logging
from datetime import datetime, timedelta

from .interfaces import Scheduler
from .utils import parse_datetime, parse_time, parse_timedelta, stringify_datetime


LOG = logging.getLogger(__name__)


def pick_schedule(name):
    if name == 'run at':
        return RunAt
    elif name == 'run every':
        return RunEvery
    else:
        raise ValueError("{!r} not a valid scheduler".format(name))


class RunEvery(Scheduler):
    DEFAULT_LAST_RUN = "1970-01-01T00:00:00Z"
    def __init__(self, config, schedule_config):
        self.config = config
        self.frequency = parse_timedelta(schedule_config['frequency'])

    def should_run(self, state):
        last_run = parse_datetime(state.get('last_run', self.DEFAULT_LAST_RUN))

        last_run_delta = datetime.utcnow() - last_run
        return last_run_delta >= self.frequency


class RunAt(Scheduler):
    DEFAULT_GRACE = "03:00:00"
    DEFAULT_LAST_RUN = "1970-01-01T00:00:00Z"
    now = datetime.utcnow

    def __init__(self, config, schedule_config):
        self.config = config
        self.target_time = parse_time(schedule_config['target_time'])
        self.grace = parse_timedelta(schedule_config.get('grace', self.DEFAULT_GRACE))

    def should_run(self, state):
        now = self.now()
        last_run = parse_datetime(state.get('last_run', self.DEFAULT_LAST_RUN))
        target_time = datetime.combine(now.date(), self.target_time)

        grace_period = target_time + self.grace

        LOG.debug("now_within_grace = %r <= %r < %r", target_time, now, grace_period)
        now_within_grace = target_time <= now < grace_period
        if not last_run:
            return now_within_grace

        LOG.debug("last_run_within_grace = %r <= %r < %r", target_time, last_run, grace_period)
        last_run_within_grace = target_time <= last_run < grace_period
        return now_within_grace and not last_run_within_grace
