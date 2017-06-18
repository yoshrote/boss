from .interfaces import ScopeFinder


def pick_scope_finder(config, scope_conf):
    type_map = {
        'hardcoded': MemoryScopeFinder,
        'sqlite': SQLScopeFinder
    }
    return type_map[task_conf['type']](config, scope_conf)


class MemoryScopeFinder(ScopeFinder):
    """ScopeFinder backed nothing.

    Example config:
    {
        'scope_finder': {
            'scopes': [
                Scope(...),
                Scope(...),
                Scope(...),
            ]
        }
    }
    """

    def __init__(self, config, scope_conf):
        self.scopes = scope_conf['scopes']

    def find(self, name):
        for scope in self.scopes.get(name, []):
            yield scope


class SQLScopeFinder(ScopeFinder):
    """ScopeFinder backed by an SQL Database.

    Example config:
    {
        'scope_finder': {
            'connection': sqlite.Connection('scopes.db'),
            'query': "SELECT * FROM scopes WHERE enabled=true"
        }
    }
    """

    def __init__(self, config, scope_conf):
        assert scope_conf['connection']['type'] == 'sqlite', "Unsupported connection type"
        self.connection = config.connections[scope_conf['connection']]
        self.query = scope_conf['query']

    def find(self, name):
        for scope in self.connection.execute(self.query, (name,)):
            yield scope
