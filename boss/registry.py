import json
import logging
from datetime import datetime

from .interfaces import Registry
from .utils import parse_datetime, stringify_datetime


LOG = logging.getLogger(__name__)


def initialize_registry(config, registry_conf):
    valid_registry_types = []
    for name, value in globals().items():
        try:
            is_registry = issubclass(value, Registry) and value is not Registry
        except TypeError:
            pass
        else:
            if is_registry:
                valid_registry_types.append(value.NAME)
                if value.NAME == registry_conf['type']:
                    return value.from_configs(config, registry_conf)

    raise ValueError(
        "unknown registry type {!r}.\n"
        "valid types: {}".format(
            registry_conf['type'], 
            valid_registry_types
        )
    )


class MemoryRegistry(Registry):
    """An ephemeral Registry."""
    NAME = "memory"

    @classmethod
    def from_configs(cls, config, registry_conf):
        """Initializes MemoryRegistry from configs.

        registry:
          type: memory
        """
        return cls()

    def __init__(self):
        self.states = {}

    def get_state(self, task, params):
        key = (task.name, frozenset(params.items()))
        response = self.states.get(key, {})
        return {} if not response else json.loads(response)

    def update_state(self, task, params):
        key = (task.name, frozenset(params.items()))
        self.states[key] = json.dumps({
            "last_run": stringify_datetime(datetime.utcnow())
        })


class SQLRegistry(Registry):
    """A sqlite backed Registry."""
    NAME = "sqlite"

    @classmethod
    def from_configs(cls, config, registry_conf):
        """Initializes SQLRegistry from configs.

        registry:
          type: sqlite
          name: boss_db
          fetch_query: SELECT state FROM registry WHERE key=?
          update_query: INSERT OR REPLACE INTO state (key, state) VALUES (?, ?)
        """
        assert registry_conf['type'] == 'sqlite', "Unsupported connection type"
        connection = config.connections[registry_conf['connection']]
        fetch_q = registry_conf['fetch_query']
        update_q = registry_conf['update_query']
        return cls(connection, fetch_q, update_q)

    def __init__(self, connection, fetch_q, update_q):
        self.connection = connection
        self.fetch_q = fetch_q
        self.update_q = update_q

    def get_state(self, task, params):
        key = json.dumps((task.name, sorted(params.items())))
        cursor = self.connection.execute(self.fetch_q, (key,))
        response = cursor.fetchone()
        cursor.close()
        return {} if not response else json.loads(response['state'])

    def update_state(self, task, params):
        key = json.dumps((task.name, sorted(params.items())))
        self.connection.execute(self.update_q, (key, json.dumps({
            "last_run": stringify_datetime(datetime.utcnow())
        })))
