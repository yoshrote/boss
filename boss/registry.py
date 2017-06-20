import json
import logging
from datetime import datetime

from .interfaces import Registry
from .utils import import_function, parse_datetime, stringify_datetime


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

    try:
        klass = import_function(registry_conf['type'])
        assert issubclass(klass, Registry) and klass is not Registry
    except (ImportError, AssertionError):
        pass
    else:
        return klass.from_configs(config, registry_conf)

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
        if not response:
            return {}
        else:
            response = json.loads(response)
            response['last_run'] = parse_datetime(response['last_run'])
            return response

    def update_state(self, task, params):
        key = (task.name, frozenset(params.items()))
        self.states[key] = json.dumps({
            "last_run": stringify_datetime(datetime.utcnow())
        })


class SQLRegistry(Registry):
    """A sqlite backed Registry."""
    NAME = "sqlite"

    @classmethod
    def create_table(cls, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE registry (
                key TEXT PRIMARY KEY,
                state TEXT
            )
            """)
            cursor.close()
        except:
            pass

    @classmethod
    def from_configs(cls, config, registry_conf):
        """Initializes SQLRegistry from configs.

        registry:
          type: sqlite
          name: boss_db
        """
        assert registry_conf['type'] == 'sqlite', "Unsupported connection type"
        connection = config.connections[registry_conf['connection']]
        cls.create_table(connection)
        return cls(connection)

    def __init__(self, connection):
        self.connection = connection
        self.fetch_q = "SELECT state FROM registry WHERE key=?"
        self.update_q = "INSERT OR REPLACE INTO state (key, state) VALUES (?, ?)"

    def get_state(self, task, params):
        key = json.dumps((task.name, sorted(params.items())))
        cursor = self.connection.execute(self.fetch_q, (key,))
        response = cursor.fetchone()
        cursor.close()
        if not response:
            return {}
        else:
            response = json.loads(response['state'])
            response['last_run'] = parse_datetime(response['last_run'])
            return response

    def update_state(self, task, params):
        key = json.dumps((task.name, sorted(params.items())))
        self.connection.execute(self.update_q, (key, json.dumps({
            "last_run": stringify_datetime(datetime.utcnow())
        })))
