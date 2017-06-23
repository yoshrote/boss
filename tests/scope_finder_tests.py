import unittest

import mock

from boss.config import Configurator
from boss.interfaces import ScopeFinder
from boss.scope_finder import initialize_scope_finder, MemoryScopeFinder, SQLScopeFinder


class SampleScopeFinder(ScopeFinder):
    NAME = 'Sample'

    @classmethod
    def from_configs(cls, config, registry_conf):
        return cls()

    def find(self, task):
        return []


class ScopeFinderTests(unittest.TestCase):
    def test_initialize_task_finder(self):
        """ Test that known and arbitrary values are handled properly"""
        mock_config = mock.Mock(autospec=Configurator)
        mock_config.connections = mock.MagicMock()

        self.assertIsInstance(
            initialize_scope_finder(mock_config, {'type': 'hardcoded', 'scopes': []}),
            MemoryScopeFinder
        )
        self.assertIsInstance(
            initialize_scope_finder(mock_config, {'type': 'sqlite', 'connection': 'test', 'query': ''}),
            SQLScopeFinder
        )
        self.assertRaises(
            ImportError,
            initialize_scope_finder, mock_config, {'type': 'task_finder.that.does.not:exist'}
        )
        self.assertRaises(
            ValueError,
            initialize_scope_finder, mock_config, {'type': 'datetime:datetime'}
        )
        self.assertIsInstance(
            initialize_scope_finder(mock_config, {'type': '{}:{}'.format(__name__, 'SampleScopeFinder')}),
            SampleScopeFinder
        )

if __name__ == '__main__':
    unittest.main()
