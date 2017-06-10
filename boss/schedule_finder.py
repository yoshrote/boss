from .interfaces import ScheduleFinder


class MemoryScheduleFinder(ScheduleFinder):
    """ScheduleFinder backed nothing.

    Example config:
    {
        'schedule_finder': {
            'schedules': [
                Schedule(...),
                Schedule(...),
                Schedule(...),
            ]
        }
    }
    """

    def __init__(self, config):
        self.schedules = config['schedule_finder']['schedules']

    def find(self):
        for schedule in self.schedules:
            yield schedule


class MongoScheduleFinder(ScheduleFinder):
    """ScheduleFinder backed by a Mongo Database.

    Example config:
    {
        'schedule_finder': {
            'connection': pymongo.MongoClient()['boss']['schedules'],
            'query': {'enabled': True}
        }
    }
    """

    def __init__(self, config):
        self.connection = config['schedule_finder']['connection']
        self.query = config['schedule_finder']['query']

    def find(self):
        for schedule in self.connection.find(self.query):
            yield schedule


class SQLScheduleFinder(ScheduleFinder):
    """ScheduleFinder backed by an SQL Database.

    Example config:
    {
        'schedule_finder': {
            'connection': sqlite.Connection('schedules.db'),
            'query': "SELECT * FROM schedules WHERE enabled=true"
        }
    }
    """

    def __init__(self, config):
        self.connection = config['schedule_finder']['connection']
        self.query = config['schedule_finder']['query']

    def find(self):
        for schedule in self.connection.execute(self.query):
            yield schedule
