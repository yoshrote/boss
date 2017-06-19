from .interfaces import TaskFinder


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
        """Initializes MemoryTaskFinder from configs.

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
    def from_configs(cls, config, task_conf):
        """Initializes SQLTaskFinder from configs.

        task_finder:
          - type: sql
            # label to reference shared connection resource
            name: boss_db
            # we want all tasks so no need to parameterize query
            query: SELECT * FROM tasks WHERE enabled=true
        """
        return cls(
            config.connections[task_conf['connection']],
            task_conf['query']
        )

    def __init__(self, connection, query):
        self.connection = connection
        self.query = query

    def find(self):
        for task in self.connection.execute(self.query):
            yield task
