from datetime import datetime, timedelta
from .interfaces import Scheduler


class RunEvery(Scheduler):
    def __init__(self, config, task_config):
        self.config = config
        self.task_config = task_config

    def should_run(self, state):
        last_run = state.get('last_run')
        if not last_run:
            return True

        last_run_delta = datetime.utcnow() - datetime.utcfromtimestamp(last_run)
        return last_run_delta >= self.task_config['frequency']


class RunAt(Scheduler):
    DEFAULT_GRACE = timedelta(hours=3)
    now = datetime.utcnow

    def __init__(self, config, task_config):
        self.config = config
        self.task_config = task_config

    def should_run(self, state):
        last_run = state.get('last_run')
        now = self.now()
        target_time = self.task_config['target_time']
        grace = self.task_config('grace', self.DEFAULT_GRACE)

        now_within_grace = target_time <= now < target_time + grace
        if not last_run:
            return now_within_grace

        last_run_within_grace = target_time <= last_run < target_time + grace
        return now_within_grace and not last_run_within_grace
