from datetime import datetime

from .interfaces import Registry


def pick_scope_finder(config, registry_conf):
    type_map = {
        'hardcoded': MemoryRegistry,
        'sqlite': SQLRegistry
    }
    return type_map[task_conf['type']](config, registry_conf)


class MemoryRegistry(Registry):
    """Registry backed nothing.

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

    def __init__(self, config, registry_conf):
        self.states = {}

    def get_state(self, task, kwargs):
        key = (task.name, frozenset(kwargs.items()))
        return self.states.get(key, {})

    def update_state(self, task, kwargs):
        key = (task.name, frozenset(kwargs.items()))
        return self.states[key] = {
            "last_run": datetime.utcnow()
        }


class SQLRegistry(Registry):
    """Registry backed by an SQL Database.

    Example config:
    {
        'registry': {
            'connection': sqlite.Connection('scopes.db'),
            'query': "SELECT * FROM scopes WHERE enabled=true"
        }
    }
    """
    DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, config, registry_conf):
        assert registry_conf['connection']['type'] == 'sqlite', "Unsupported connection type"
        self.connection = config.connections[registry_conf['connection']]
        self.fetch_q = registry_conf['fetch_query']
        self.update_q = registry_conf['update_query']

    def get_state(self, task, kwargs):
        key = json.dumps((task.name, sorted(kwargs.items())))
        cursor = self.connection.execute(self.fetch_q, (key,))
        response = cursor.fetchone()
        cursor.close()
        if not response:
            return {}
        else:
            response = json.loads(response['state'])
            response['last_run'] = datetime.strptime(response['last_run'], self.DT_FORMAT)

    def update_state(self, task, kwargs):
        key = json.dumps((task.name, sorted(kwargs.items())))
        self.connection.execute(self.update_q, (key, json.dumps({
            "last_run": datetime.utcnow().strftime(self.DT_FORMAT)
        })))
