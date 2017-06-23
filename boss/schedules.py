import logging
from datetime import datetime

from .interfaces import Scheduler
from .utils import import_function, parse_datetime, parse_time, parse_timedelta


LOG = logging.getLogger(__name__)


def pick_schedule(config, schedule_config):
    name = schedule_config['type']
    if name == 'run at':
        return RunAt.from_config(config, schedule_config)
    elif name == 'run every':
        return RunEvery.from_config(config, schedule_config)
    else:
        try:
            klass = import_function(name)
            assert issubclass(klass, Scheduler) and klass is not Scheduler
            return klass.from_config(config, schedule_config)
        except (ImportError, AssertionError):
            raise ValueError("{!r} not a valid scheduler".format(name))


class RunEvery(Scheduler):
    DEFAULT_LAST_RUN = "1970-01-01T00:00:00Z"
    now = datetime.utcnow

    @classmethod
    def from_config(cls, config, schedule_config):
        frequency = parse_timedelta(schedule_config['frequency'])
        return cls(frequency)

    def __init__(self, frequency):
        self.frequency = frequency

    def should_run(self, state):
        last_run = parse_datetime(state.get('last_run', self.DEFAULT_LAST_RUN))

        last_run_delta = self.now() - last_run
        return last_run_delta >= self.frequency


class RunAt(Scheduler):
    DEFAULT_GRACE = "03:00:00"
    DEFAULT_LAST_RUN = "1970-01-01T00:00:00Z"
    now = datetime.utcnow

    @classmethod
    def from_config(cls, config, schedule_config):
        target_time = parse_time(schedule_config['target_time'])
        grace = parse_timedelta(schedule_config.get('grace', cls.DEFAULT_GRACE))
        return cls(target_time, grace)

    def __init__(self, target_time, grace):
        self.target_time = target_time
        self.grace = grace

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
