import json
import unittest

import mock

from boss.config import Configurator
from boss.scope_finder import (
    initialize_scope_finder,
    MemoryScopeFinder,
    SQLScopeFinder
)


class ScopeFinderTests(unittest.TestCase):
    def test_initialize_task_finder(self):
        """ Test that known and arbitrary values are handled properly"""
        mock_config = mock.Mock(spec=Configurator)
        mock_config.connections = mock.MagicMock()

        self.assertIsInstance(
            initialize_scope_finder(
                mock_config,
                {'type': 'hardcoded', 'scopes': []}
            ),
            MemoryScopeFinder
        )
        self.assertIsInstance(
            initialize_scope_finder(
                mock_config,
                {'type': 'sqlite', 'connection': 'test'}
            ),
            SQLScopeFinder
        )
        self.assertRaises(
            ValueError,
            initialize_scope_finder,
            mock_config, {'type': 'task_finder.that.does.not:exist'}
        )
        self.assertRaises(
            ValueError,
            initialize_scope_finder,
            mock_config, {'type': 'datetime:datetime'}
        )

    @mock.patch('sqlite3.Connection')
    def test_sql_find(self, sql_mock):
        """ Test SQLScopeFinder.find"""
        mock_config = mock.Mock(spec=Configurator)
        mock_config.connections = {'test': sql_mock}
        scope_config = {'type': 'sqlite', 'connection': 'test'}
        scope_finder = SQLScopeFinder.from_configs(
            mock_config,
            scope_config
        )

        cursor_mock = sql_mock.cursor.return_value
        cursor_mock.execute.return_value = iter([
            {'params': json.dumps({'foo': 1})},
            {'params': json.dumps({'foo': 2})}
        ])

        scope_name = 'foo'
        self.assertEqual(
            sorted(scope_finder.find(scope_name), key=lambda x: x['foo']),
            [{'foo': 1}, {'foo': 2}]
        )

    def test_memory_find(self):
        """ Test MemoryScopeFinder.find"""
        mock_config = mock.Mock(spec=Configurator)
        scope_config = {
            'type': 'hardcoded',
            'scopes': {
                'foo': [
                    {'foo': 1},
                    {'foo': 2}
                ]
            }
        }
        scope_finder = MemoryScopeFinder.from_configs(
            mock_config,
            scope_config
        )
        self.assertEqual(
            sorted(scope_finder.find('foo'), key=lambda x: x['foo']),
            [{'foo': 1}, {'foo': 2}]
        )


if __name__ == '__main__':
    unittest.main()
