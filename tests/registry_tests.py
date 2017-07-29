import json
import unittest
from datetime import datetime

import mock

from boss.config import Configurator

from boss.registry import initialize_registry, MemoryRegistry, SQLRegistry
from boss.utils import stringify_datetime


class DummyTask(object):
    def __init__(self, name):
        self.name = name


class RegistryTests(unittest.TestCase):
    def test_initialize_registry(self):
        """ Test that known and arbitrary values are handled properly"""
        mock_config = mock.Mock(autospec=Configurator)
        mock_config.connections = mock.MagicMock()

        self.assertIsInstance(
            initialize_registry(mock_config, {'type': 'memory'}),
            MemoryRegistry
        )
        self.assertIsInstance(
            initialize_registry(mock_config, {'type': 'sqlite', 'connection': 'test'}),
            SQLRegistry
        )
        self.assertRaises(
            ValueError,
            initialize_registry, mock_config, {'type': 'registry.that.does.not:exist'}
        )
        self.assertRaises(
            ValueError,
            initialize_registry, mock_config, {'type': 'datetime:datetime'}
        )

    @mock.patch('sqlite3.Connection')
    def test_sql_get_state_blank(self, sql_mock):
        """ Test SQLRegistry.get_state"""
        mock_config = mock.Mock(spec=Configurator)
        mock_config.connections = {'test': sql_mock}
        registry_config = {'type': 'sqlite', 'connection': 'test'}
        registry = SQLRegistry.from_configs(
            mock_config,
            registry_config
        )

        cursor_mock = sql_mock.cursor.return_value
        cursor_mock.fetchone.return_value = None
        self.assertEqual(
            registry.get_state(DummyTask('foo'), {'foo': 1}),
            {}
        )

    @mock.patch('sqlite3.Connection')
    def test_sql_get_state_exists(self, sql_mock):
        """ Test SQLRegistry.get_state when a state exists"""
        mock_config = mock.Mock(spec=Configurator)
        mock_config.connections = {'test': sql_mock}
        registry_config = {'type': 'sqlite', 'connection': 'test'}
        registry = SQLRegistry.from_configs(
            mock_config,
            registry_config
        )

        last_run = datetime.utcnow().replace(microsecond=0)
        cursor_mock = sql_mock.cursor.return_value
        cursor_mock.fetchone.return_value = {
            'state': json.dumps({u'last_run': stringify_datetime(last_run)})
        }

        self.assertEqual(
            registry.get_state(DummyTask('foo'), {'foo': 1}),
            {u'last_run': last_run}
        )

    @mock.patch('sqlite3.Connection')
    def test_sql_update_state(self, sql_mock):
        """ Test SQLRegistry.update_state"""
        mock_config = mock.Mock(spec=Configurator)
        mock_config.connections = {'test': sql_mock}
        registry_config = {'type': 'sqlite', 'connection': 'test'}
        registry = SQLRegistry.from_configs(
            mock_config,
            registry_config
        )

        registry.now = lambda: datetime.utcnow().replace(microsecond=0)
        key = registry.build_key(DummyTask('foo'), {'foo': 1})
        registry.update_state(DummyTask('foo'), {'foo': 1})

        cursor_mock = sql_mock.cursor.return_value
        cursor_mock.execute.assert_called_with(
            registry.update_q, (
                key,
                json.dumps({u'last_run': stringify_datetime(registry.now())})
            )
        )

    def test_memory_get_state_blank(self):
        """ Test MemoryRegistry.get_state when no state exists"""
        mock_config = mock.Mock(spec=Configurator)
        registry_config = {'type': 'memory'}
        registry = MemoryRegistry.from_configs(
            mock_config,
            registry_config
        )

        self.assertEqual(
            registry.get_state(DummyTask('foo'), {'foo': 1}),
            {}
        )

    def test_memory_get_state_exists(self):
        """ Test MemoryRegistry.get_state when a state exists"""
        mock_config = mock.Mock(spec=Configurator)
        registry_config = {'type': 'memory'}
        registry = MemoryRegistry.from_configs(
            mock_config,
            registry_config
        )

        last_run = datetime.utcnow().replace(microsecond=0)
        registry.states[('foo', frozenset([('foo', 1)]))] = json.dumps(
            {u'last_run': stringify_datetime(last_run)}
        )

        self.assertEqual(
            registry.get_state(DummyTask('foo'), {'foo': 1}),
            {u'last_run': last_run}
        )

    def test_memory_update_state(self):
        """ Test MemoryRegistry.update_state"""
        mock_config = mock.Mock(spec=Configurator)
        registry_config = {'type': 'memory'}
        registry = MemoryRegistry.from_configs(
            mock_config,
            registry_config
        )

        registry.now = lambda: datetime.utcnow().replace(microsecond=0)
        registry.update_state(DummyTask('foo'), {'foo': 1})
        self.assertEqual(
            registry.states[registry.build_key(DummyTask('foo'), {'foo': 1})],
            json.dumps({'last_run': stringify_datetime(registry.now())})
        )
