import logging
import time
from .task import Task

LOG = logging.getLogger(__name__)


class Application(object):
    """Configure and encapsulates the main loop."""

    Task = Task

    def __init__(self, config, registry):
        """
        Initialize `Application`.

        Expects a dict-like objects `config`
        """
        self.config = config
        self.registry = registry

    def run(self):
        """Main run loop."""
        while True:
            LOG.debug("starting loop iteration")
            for task_params in self.config.find_task_params():
                LOG.debug("task_params: %r", task_params)
                task = self.Task(self.config, task_params)
                scheduler = task.scheduler
                for params in self.config.find_params(task):
                    LOG.debug("params: %r", params)
                    state = self.registry.get_state(task, params)
                    LOG.debug("state: %r", state)
                    if scheduler.should_run(state):
                        LOG.info("about to run %s(%r)", task.name, params)
                        self.registry.update_state(task, params)
                        task.run(params)
                        time.sleep(1)
            time.sleep(10)
