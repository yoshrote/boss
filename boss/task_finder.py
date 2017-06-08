from .interfaces import TaskFinder


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

    def __init__(self, config):
        self.tasks = config['task_finder']['tasks']

    def find_tasks(self):
        for task in self.tasks:
            yield task


class MongoTaskFinder(TaskFinder):
    """TaskFinder backed by a Mongo Database.

    Example config:
    {
        'task_finder': {
            'connection': pymongo.MongoClient()['boss']['tasks'],
            'query': {'enabled': True}
        }
    }
    """

    def __init__(self, config):
        self.connection = config['task_finder']['connection']
        self.query = config['task_finder']['query']

    def find_tasks(self):
        for task in self.connection.find(self.query):
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

    def __init__(self, config):
        self.connection = config['task_finder']['connection']
        self.query = config['task_finder']['query']

    def find_tasks(self):
        for task in self.connection.execute(self.query):
            yield task
