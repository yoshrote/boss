class TaskFinder(object):
    def find_tasks(self):
        raise NotImplementedError('find_tasks')


class ParameterFinder(object):
    def parameters(self):
        raise NotImplementedError('parameters')


class Task(object):
    def run(self, args, kwargs):
        raise NotImplementedError('run')


class ScheduleFinder(object):
    def find_schedules(self):
        raise NotImplementedError('find_schedules')


class Scheduler(object):
    def should_run(self, task, state):
        raise NotImplementedError('should_run')


class Registry(object):
    def get_state(self, task, args, kwargs):
        raise NotImplementedError('get_state')

    def update_state(self, task, args, kwargs):
        raise NotImplementedError('update_state')
