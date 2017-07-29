from abc import ABCMeta, abstractmethod


class TaskFinder(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def from_configs(cls, config, task_conf):  # pragma: no cover
        return None

    @abstractmethod
    def find(self):  # pragma: no cover
        return []


class ScopeFinder(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def from_configs(cls, config, scope_conf):  # pragma: no cover
        raise NotImplementedError('from_configs')

    @abstractmethod
    def find(self, task):  # pragma: no cover
        raise NotImplementedError('find')


class Scheduler(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def from_configs(cls, config, schedule_conf):  # pragma: no cover
        raise NotImplementedError('from_configs')

    @abstractmethod
    def should_run(self, state):  # pragma: no cover
        raise NotImplementedError('should_run')


class Registry(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def from_configs(cls, config, registry_conf):  # pragma: no cover
        raise NotImplementedError('from_configs')

    @abstractmethod
    def get_state(self, task, params):  # pragma: no cover
        raise NotImplementedError('get_state')

    @abstractmethod
    def update_state(self, task, params):  # pragma: no cover
        raise NotImplementedError('update_state')
