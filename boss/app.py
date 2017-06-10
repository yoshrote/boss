class Application(object):
    """Configure and encapsulates the main loop."""

    TaskFinder = None
    Task = None
    ParameterFinder = None
    ScheduleFinder = None
    Scheduler = None
    Registry = None

    def __init__(self, config):
        """
        Initialize `Application`.

        Expects a dict-like objects `config`
        """
        self.config = config
        self.task_finder = self.TaskFinder(self.config)
        self.schedule_finder = self.ScheduleFinder(self.config)
        self.parameter_finder = self.ParameterFinder(self.config)
        self.registry = self.Registry(self.config)

    def run(self):
        """Main run loop."""
        while True:
            for task_params in self.task_finder.find():
                task = self.Task(self.config, task_params)
                scheduler = task.build_schedule()
                for args, kwargs in self.parameter_finder.find(task):
                    state = self.registry.get_state(task, args, kwargs)
                    if scheduler.should_run(state):
                        self.registry.update_state(task, args, kwargs)
                        task.run(args, kwargs)
