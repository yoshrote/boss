import json

from .interfaces import TaskFinder
from .utils import import_function


def initialize_task_finder(config, task_conf):
    valid_task_finder_types = []
    for name, value in globals().items():
        try:
            is_task_finder = issubclass(value, TaskFinder) and value is not TaskFinder
        except TypeError:
            pass
        else:
            if is_task_finder:
                valid_task_finder_types.append(value.NAME)
                if value.NAME == task_conf['type']:
                    return value.from_configs(config, task_conf)

    try:
        klass = import_function(task_conf['type'])
        assert issubclass(klass, TaskFinder) and klass is not TaskFinder
    except (ImportError, AssertionError):
        pass
    else:
        return klass.from_configs(config, task_conf)

    raise ValueError(
        "unknown task type {!r}.\n"
        "valid types: {}".format(
            task_conf['type'],
            valid_task_finder_types
        )
    )


class MemoryTaskFinder(TaskFinder):
    """TaskFinder whose tasks are enumerated in configs."""

    NAME = 'hardcoded'

    @classmethod
    def from_configs(cls, config, task_conf):
        """Initialize MemoryTaskFinder from configs.

        task_finder:
            - type: hardcoded
              tasks:
                - Task(...)
                - Task(...)
        """
        return cls(task_conf['tasks'])

    def __init__(self, tasks):
        """Find tasks directly from config."""
        self.tasks = tasks

    def find(self):
        for task in self.tasks:
            yield task


class SQLTaskFinder(TaskFinder):
    """TaskFinder backed by an SQL Database."""

    NAME = 'sqlite'

    @classmethod
    def create_table(cls, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task TEXT,
                enabled BOOLEAN,
            )
            """)
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS enabled_tasks
            ON tasks (enabled)
            """)
            cursor.close()
        except:
            pass

    @classmethod
    def from_configs(cls, config, task_conf):
        """Initialize SQLTaskFinder from configs.

        task_finder:
          - type: sql
            name: boss_db
        """
        connection = config.connections[task_conf['connection']]
        cls.create_table(connection)
        return cls(
            connection,
            task_conf['query']
        )

    def __init__(self, connection, query):
        self.connection = connection
        self.query = "SELECT task FROM tasks WHERE enabled=true"

    def find(self):
        for row in self.connection.execute(self.query):
            yield json.loads(row['task'])
