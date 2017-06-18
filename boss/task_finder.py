from .interfaces import TaskFinder


def pick_task_finder(config, task_conf):
    type_map = {
        'hardcoded': MemoryTaskFinder,
        'sqlite': SQLTaskFinder
    }
    return type_map[task_conf['type']](config, task_conf)


class MemoryTaskFinder(TaskFinder):
    """TaskFinder backed nothing.

    Example config:
    {
        'task_finder': {
            'tasks': [
                Task(...),
                Task(...),
                Task(...),
            ]
        }
    }
    """

    def __init__(self, config, task_conf):
        self.tasks = task_conf['tasks']

    def find(self):
        for task in self.tasks:
            yield task


class SQLTaskFinder(TaskFinder):
    """TaskFinder backed by an SQL Database.

    Example config:
    {
        'task_finder': {
            'connection': sqlite.Connection('tasks.db'),
            'query': "SELECT * FROM tasks WHERE enabled=true"
        }
    }
    """

    def __init__(self, config, task_conf):
        assert task_conf['connection']['type'] == 'sqlite', "Unsupported connection type"
        self.connection = config.connections[task_conf['connection']]
        self.query = task_conf['query']

    def find(self, name):
        for task in self.connection.execute(self.query):
            yield task
