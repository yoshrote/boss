import json
import unittest

import mock

from boss.config import Configurator
from boss.task_finder import initialize_task_finder, MemoryTaskFinder, SQLTaskFinder


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
            ValueError,
            initialize_task_finder, mock_config, {'type': 'task_finder.that.does.not:exist'}
        )
        self.assertRaises(
            ValueError,
            initialize_task_finder, mock_config, {'type': 'datetime:datetime'}
        )

    @mock.patch('sqlite3.Connection')
    def test_sql_find(self, sql_mock):
        """ Test SQLTaskFinder.find"""
        mock_config = mock.Mock(spec=Configurator)
        mock_config.connections = {'test': sql_mock}
        task_config = {'type': 'sqlite', 'connection': 'test'}
        task_finder = SQLTaskFinder.from_configs(
            mock_config,
            task_config
        )

        cursor_mock = sql_mock.cursor.return_value
        cursor_mock.execute.return_value = iter([
            {'task': json.dumps({'foo': 1})},
            {'task': json.dumps({'foo': 2})}
        ])

        self.assertItemsEqual(
            list(task_finder.find()),
            [{'foo': 1}, {'foo': 2}]
        )

    def test_memory_find(self):
        """ Test MemoryTaskFinder.find"""
        mock_config = mock.Mock(spec=Configurator)
        task_config = {
            'type': 'hardcoded',
            'tasks': [
                {'foo': 1},
                {'foo': 2}
            ]
        }
        task_finder = MemoryTaskFinder.from_configs(
            mock_config,
            task_config
        )
        self.assertItemsEqual(
            list(task_finder.find()),
            [{'foo': 1}, {'foo': 2}]
        )

if __name__ == '__main__':
    unittest.main()
