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
            schedules = self.schedule_finder.find_schedules()
            for task in self.task_finder.find_tasks():
                scheduler = task.pick_schedule(schedules)
                for args, kwargs in self.parameter_finder.parameters(task):
                    state = self.registry.get_state(task, args, kwargs)
                    if scheduler.should_run(task, state):
                        self.registry.update_state(task, args, kwargs)
                        task.run(args, kwargs)
