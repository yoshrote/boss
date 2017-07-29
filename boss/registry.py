import json
import logging
from datetime import datetime

from .interfaces import Registry
from .utils import (
    get_class_from_type_value,
    parse_datetime,
    stringify_datetime
)


LOG = logging.getLogger(__name__)


def initialize_registry(config, registry_conf):
    return get_class_from_type_value(
        'registry',
        Registry,
        registry_conf,
        config
    )


class MemoryRegistry(Registry):
    """An ephemeral Registry."""
    now = datetime.utcnow

    @classmethod
    def from_configs(cls, config, registry_conf):
        """Initialize MemoryRegistry from configs.

        registry:
          type: memory
        """
        return cls()

    def __init__(self):
        self.states = {}

    def build_key(self, task, params):
        return (task.name, frozenset(params.items()))

    def get_state(self, task, params):
        key = self.build_key(task, params)
        response = self.states.get(key, {})
        if not response:
            return {}
        else:
            response = json.loads(response)
            response['last_run'] = parse_datetime(response['last_run'])
            return response

    def update_state(self, task, params):
        key = self.build_key(task, params)
        self.states[key] = json.dumps({
            "last_run": stringify_datetime(self.now())
        })


class SQLRegistry(Registry):
    """A sqlite backed Registry."""
    now = datetime.utcnow

    @classmethod
    def create_table(cls, connection):
        cursor = connection.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS registry (
                key TEXT PRIMARY KEY,
                state TEXT
            )
            """)
        finally:
            cursor.close()

    @classmethod
    def from_configs(cls, config, registry_conf):
        """Initialize SQLRegistry from configs.

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
        key = self.build_key(task, params)
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.fetch_q, (key,))
            response = cursor.fetchone()
        finally:
            cursor.close()

        if not response:
            return {}
        else:
            response = json.loads(response['state'])
            response['last_run'] = parse_datetime(response['last_run'])
            return response

    def build_key(self, task, params):
        return json.dumps((task.name, sorted(params.items())))

    def update_state(self, task, params):
        key = self.build_key(task, params)
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.update_q, (key, json.dumps({
                "last_run": stringify_datetime(self.now())
            })))
        finally:
            cursor.close()
