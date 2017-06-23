from abc import ABCMeta, abstractmethod, abstractproperty


class TaskFinder(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def NAME(self):
        return None

    @classmethod
    @abstractmethod
    def from_configs(cls, config, task_conf):
        return None

    @abstractmethod
    def find(self):
        return []


class ScopeFinder(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def NAME(self):
        return None

    @classmethod
    @abstractmethod
    def from_configs(cls, config, scope_conf):
        raise NotImplementedError('from_configs')

    @abstractmethod
    def find(self, task):
        raise NotImplementedError('find')


class Scheduler(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def from_configs(cls, config, schedule_conf):
        raise NotImplementedError('from_configs')

    @abstractmethod
    def should_run(self, state):
        raise NotImplementedError('should_run')


class Registry(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def NAME(self):
        return None

    @classmethod
    @abstractmethod
    def from_configs(cls, config, registry_conf):
        raise NotImplementedError('from_configs')

    @abstractmethod
    def get_state(self, task, params):
        raise NotImplementedError('get_state')

    @abstractmethod
    def update_state(self, task, params):
        raise NotImplementedError('update_state')
