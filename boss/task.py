import logging

from .schedules import pick_schedule
from .utils import import_function, request_maker


LOG = logging.getLogger(__name__)


class Task(object):
    def __init__(self, config, task_config):
        self.config = config
        self.name = task_config['name']
        self.scope = task_config['scope']

        self.scheduler = self.build_schedule(task_config['schedule'])
        self.func = self.build_func(task_config['function'])

    def build_schedule(self, schedule_config):
        schedule_klass = pick_schedule(
            schedule_config['type']
        )
        return schedule_klass(
            self.config, schedule_config['params']
        )

    def build_func(self, func_config):
        LOG.debug("building function: %r", func_config)
        func_type = func_config['type']
        if func_type == 'local':
            return import_function(func_config['target'])
        elif func_type == 'remote':
            return request_maker(func_config['target'])
        else:
            raise ValueError("{!r} is not a valid function type".format(func_type))

    def run(self, params):
        self.func(params)
