from datetime import datetime

from .interfaces import Registry


class MemoryRegistry(Registry):
	def __init__(self, config):
		self.states = {}

    def get_state(self, task, kwargs):
    	key = (task.name, frozenset(kwargs.items()))
    	return self.states.get(key, {})

    def update_state(self, task, kwargs):
    	key = (task.name, frozenset(kwargs.items()))
    	return self.states[key] = {
    		"last_run": datetime.utcnow()
    	}
