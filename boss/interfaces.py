class TaskFinder(object):
    NAME = None
    
    @classmethod
    def from_configs(cls, config, task_conf):
        raise NotImplementedError('from_configs')

    def find(self):
        raise NotImplementedError('find')


class ScopeFinder(object):
    NAME = None
    
    @classmethod
    def from_configs(cls, config, scope_conf):
        raise NotImplementedError('from_configs')

    def find(self, task):
        raise NotImplementedError('find')


class Scheduler(object):
    def should_run(self, state):
        raise NotImplementedError('should_run')


class Registry(object):
    NAME = None

    @classmethod
    def from_configs(cls, config, registry_conf):
        raise NotImplementedError('from_configs')

    def get_state(self, task, params):
        raise NotImplementedError('get_state')

    def update_state(self, task, params):
        raise NotImplementedError('update_state')
