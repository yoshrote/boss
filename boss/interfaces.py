class TaskFinder(object):
    def find(self):
        raise NotImplementedError('find')


class ParameterFinder(object):
    def find(self, task):
        raise NotImplementedError('find')


class ScheduleFinder(object):
    def find(self):
        raise NotImplementedError('find')


class Scheduler(object):
    def should_run(self, state):
        raise NotImplementedError('should_run')


class Registry(object):
    def get_state(self, task, kwargs):
        raise NotImplementedError('get_state')

    def update_state(self, task, kwargs):
        raise NotImplementedError('update_state')
