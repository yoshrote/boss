from datetime import datetime, timedelta

from .interfaces import Scheduler

def pick_schedule(name):
    if name == 'run at':
        return RunAt
    elif name == 'run every':
        return RunEvery
    else:
        raise ValueError("{!r} not a valid scheduler".format(name))


class RunEvery(Scheduler):
    def __init__(self, config, schedule_config):
        self.config = config
        self.frequency = schedule_config['frequency']

    def should_run(self, state):
        last_run = state.get('last_run')
        if not last_run:
            return True

        last_run_delta = datetime.utcnow() - datetime.utcfromtimestamp(last_run)
        return last_run_delta >= self.frequency


class RunAt(Scheduler):
    DEFAULT_GRACE = timedelta(hours=3)
    now = datetime.utcnow

    def __init__(self, config, schedule_config):
        self.config = config
        self.target_time = schedule_config['target_time']
        self.grace = schedule_config.get('grace', self.DEFAULT_GRACE)

    def should_run(self, state):
        last_run = state.get('last_run')
        now = self.now()
        target_time = self.target_time

        grace_period = target_time + self.grace

        now_within_grace = target_time <= now < grace_period
        if not last_run:
            return now_within_grace

        last_run_within_grace = target_time <= last_run < grace_period
        return now_within_grace and not last_run_within_grace
