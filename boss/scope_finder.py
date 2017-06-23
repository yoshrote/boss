import json

from .interfaces import ScopeFinder
from .utils import get_class_from_type_value


def initialize_scope_finder(config, scope_conf):
    return get_class_from_type_value(
        'scope',
        ScopeFinder,
        scope_conf,
        config,
        globals()
    )


class MemoryScopeFinder(ScopeFinder):
    """ScopeFinder whose scopes are enumerated in configs."""

    NAME = "hardcoded"

    @classmethod
    def from_configs(cls, config, scope_conf):
        """Initialize MemoryScopeFinder from configs.

        scope_finder:
            - type: hardcoded
              scopes:
                scope1:
                  - Scope(...)
                  - Scope(...)
                scope2:
                  - Scope(...)
        """
        return cls(scope_conf['scopes'])

    def __init__(self, scopes):
        """Find scopes directly from config."""
        self.scopes = scopes

    def find(self, name):
        for scope in self.scopes.get(name, []):
            yield scope


class SQLScopeFinder(ScopeFinder):
    """ScopeFinder backed by an SQL Database."""

    NAME = "sqlite"

    @classmethod
    def create_table(cls, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scopes (
                name TEXT PRIMARY KEY,
                params TEXT,
            )
            """)
            cursor.close()
        except:
            pass

    @classmethod
    def from_configs(cls, config, scope_conf):
        """Initialize SQLScopeFinder from configs.

        scope_finder:
            - type: connection
              name: boss_db
        """
        connection = config.connections[scope_conf['connection']]
        cls.create_table(connection)
        return cls(connection)

    def __init__(self, connection):
        self.connection = connection
        self.query = "SELECT params FROM scope WHERE name=?"

    def find(self, name):
        for row in self.connection.execute(self.query, (name,)):
            yield json.loads(row['params'])
