import logging
import sqlite3
import yaml

from .registry import initialize_registry
from .scope_finder import initialize_scope_finder
from .task_finder import initialize_task_finder


LOG = logging.getLogger(__name__)


class Configurator(object):
    def __init__(self, connections=None, task_configs=None, scope_configs=None, registry_config=None):
        self.connections = {}
        self.task_configs = task_configs or []
        self.scope_configs = scope_configs or []
        self.registry_config = registry_config or {}
        self._registry = None
        self._task_finders = None
        self._scope_finders = None

        for conn_name, values in (connections or {}).iteritems():
            if values['type'] == 'sqlite':
                self.connections[conn_name] = sqlite3.connect(values['connection'])

    @property
    def registry(self):
        if not self._registry:
            LOG.info('initializing registry: %r', self.registry_config)
            self._registry = initialize_registry(self, self.registry_config)
        return self._registry

    @property
    def task_finders(self):
        if not self._task_finders:
            self._task_finders = []
            for task_conf in self.task_configs:
                LOG.info('initializing task finder: %r', task_conf)
                self._task_finders.append(
                    initialize_task_finder(self, task_conf)
                )
        return self._task_finders

    @property
    def scope_finders(self):
        if not self._scope_finders:
            self._scope_finders = []
            for scope_conf in self.scope_configs:
                LOG.info('initializing scope finder: %r', scope_conf)
                self._scope_finders.append(
                    initialize_scope_finder(self, scope_conf)
                )
        return self._scope_finders

    @classmethod
    def from_file(cls, filepath):
        with open(filepath) as f:
            data = yaml.load(f)

        connection_configs = data.get('connections', {})
        task_finder_configs = data['task_finder']
        scope_finder_configs = data['scope_finder']
        registry_config = data['registry']

        return cls(
            connections=connection_configs,
            task_configs=task_finder_configs,
            scope_configs=scope_finder_configs,
            registry_config=registry_config
        )

    def find_task_params(self):
        for task_finder in self.task_finders:
            for task_param in task_finder.find():
                yield task_param

    def find_params(self, task):
        for scope_finder in self.scope_finders:
            for params in scope_finder.find(task.scope):
                yield params
