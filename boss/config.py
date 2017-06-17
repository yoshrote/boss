import sqlite3
import yaml


class Configurator(object):
    def __init__(self, connections=None, task_finders=None, scope_finders=None):
        self.connections = {}
        self.task_finders = task_finders or []
        self.scope_finders = scope_finders or []

        for conn_name, values in (connections or {}).iteritems():
            if values['type'] == 'sqlite':
                self.connections[conn_name] = sqlite3.connect(values['connection'])

    @classmethod
    def from_file(cls, filepath):
        with open(filepath) as f:
            data = yaml.load(f)

        connection_configs = data.get('connections', {})
        task_finder_configs = data['task_finder']
        scope_finder_configs = data['scope_finder']

        return cls(
            connections=connection_configs,
            task_finders=task_finder_configs,
            scope_finders=scope_finder_configs
        )

    def find_tasks(self):
        for task_finder in self.task_finders:
            for task in task_finder.find():
                yield task

    def find_params(self, task):
        for scope_finder in self.scope_finders:
            for params in scope_finder.find(task.scope):
                yield params
