class Application(object):
    """Configure and encapsulates the main loop."""

    TaskFinder = None
    Task = None
    ParameterFinder = None
    Registry = None

    def __init__(self, config):
        """
        Initialize `Application`.

        Expects a dict-like objects `config`
        """
        self.config = config
        self.task_finder = self.TaskFinder(self.config)
        self.parameter_finder = self.ParameterFinder(self.config)
        self.registry = self.Registry(self.config)

    def run(self):
        """Main run loop."""
        while True:
            for task_params in self.task_finder.find():
                task = self.Task(self.config, task_params)
                scheduler = task.scheduler
                for kwargs in self.parameter_finder.find(task):
                    state = self.registry.get_state(task, kwargs)
                    if scheduler.should_run(state):
                        self.registry.update_state(task, kwargs)
                        task.run(kwargs)
