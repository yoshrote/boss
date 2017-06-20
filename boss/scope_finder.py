import json

from .interfaces import ScopeFinder
from .utils import import_function


def initialize_scope_finder(config, scope_conf):
    valid_scope_finder_types = []
    for name, value in globals().items():
        try:
            is_scope_finder = issubclass(value, ScopeFinder) and value is not ScopeFinder
        except TypeError:
            pass
        else:
            if is_scope_finder:
                valid_scope_finder_types.append(value.NAME)
                if value.NAME == scope_conf['type']:
                    return value.from_configs(config, scope_conf)

    try:
        klass = import_function(scope_conf['type'])
        assert issubclass(klass, ScopeFinder) and klass is not ScopeFinder
    except (ImportError, AssertionError):
        pass
    else:
        return klass.from_configs(config, scope_conf)

    raise ValueError(
        "unknown scope type {!r}.\n"
        "valid types: {}".format(
            scope_conf['type'],
            valid_scope_finder_types
        )
    )


class MemoryScopeFinder(ScopeFinder):
    """ScopeFinder whose scopes are enumerated in configs."""
    NAME = "hardcoded"

    @classmethod
    def from_configs(cls, config, scope_conf):
        """Initializes MemoryScopeFinder from configs.

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
            CREATE TABLE scopes (
                name TEXT PRIMARY KEY,
                params TEXT,
            )
            """)
            cursor.close()
        except:
            pass

    @classmethod
    def from_configs(cls, config, scope_conf):
        """Initializes SQLScopeFinder from configs.

        scope_finder:
            - type: connection
              name: boss_db
        """
        connection = config.connections[scope_conf['name']]
        cls.create_table(connection)
        return cls(connection)

    def __init__(self, connection):
        self.connection = connection
        self.query = "SELECT params FROM scope WHERE name=?"

    def find(self, name):
        for row in self.connection.execute(self.query, (name,)):
            yield json.loads(row['params'])
