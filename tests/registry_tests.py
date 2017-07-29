import unittest

import mock

from boss.config import Configurator

from boss.registry import initialize_registry, MemoryRegistry, SQLRegistry


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
