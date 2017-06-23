import unittest

import mock

from boss.config import Configurator
from boss.interfaces import TaskFinder
from boss.task_finder import initialize_task_finder, MemoryTaskFinder, SQLTaskFinder


class SampleTaskFinder(TaskFinder):
    NAME = 'Sample'

    @classmethod
    def from_configs(cls, config, registry_conf):
        return cls()

    def find(self):
        return []


class TaskFinderTests(unittest.TestCase):
    def test_initialize_task_finder(self):
        """ Test that known and arbitrary values are handled properly"""
        mock_config = mock.Mock(autospec=Configurator)
        mock_config.connections = mock.MagicMock()

        self.assertIsInstance(
            initialize_task_finder(mock_config, {'type': 'hardcoded', 'tasks': []}),
            MemoryTaskFinder
        )
        self.assertIsInstance(
            initialize_task_finder(mock_config, {'type': 'sqlite', 'connection': 'test', 'query': ''}),
            SQLTaskFinder
        )
        self.assertRaises(
            ImportError,
            initialize_task_finder, mock_config, {'type': 'task_finder.that.does.not:exist'}
        )
        self.assertRaises(
            ValueError,
            initialize_task_finder, mock_config, {'type': 'datetime:datetime'}
        )
        self.assertIsInstance(
            initialize_task_finder(mock_config, {'type': '{}:SampleTaskFinder'.format(__name__)}),
            SampleTaskFinder
        )

if __name__ == '__main__':
    unittest.main()
