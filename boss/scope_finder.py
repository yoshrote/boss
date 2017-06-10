from .interfaces import ScopeFinder


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

    def __init__(self, config):
        self.scopes = config['scope_finder']['scopes']

    def find(self):
        for scope in self.scopes:
            yield scope


class MongoScopeFinder(ScopeFinder):
    """ScopeFinder backed by a Mongo Database.

    Example config:
    {
        'scope_finder': {
            'connection': pymongo.MongoClient()['boss']['scopes'],
            'query': {'enabled': True}
        }
    }
    """

    def __init__(self, config):
        self.connection = config['scope_finder']['connection']
        self.query = config['scope_finder']['query']

    def find(self):
        for scope in self.connection.find(self.query):
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

    def __init__(self, config):
        self.connection = config['scope_finder']['connection']
        self.query = config['scope_finder']['query']

    def find(self):
        for scope in self.connection.execute(self.query):
            yield scope
