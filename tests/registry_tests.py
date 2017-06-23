import unittest

import mock

from boss.config import Configurator
from boss.interfaces import Registry
from boss.registry import initialize_registry, MemoryRegistry, SQLRegistry


class SampleRegistry(Registry):
    NAME = 'Sample'

    @classmethod
    def from_configs(cls, config, registry_conf):
        return cls()

    def get_state(self, task, params):
        return {}

    def update_state(self, task, params):
        pass


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
            ImportError,
            initialize_registry, mock_config, {'type': 'registry.that.does.not:exist'}
        )
        self.assertRaises(
            ValueError,
            initialize_registry, mock_config, {'type': 'datetime:datetime'}
        )
        self.assertIsInstance(
            initialize_registry(mock_config, {'type': '{}:SampleRegistry'.format(__name__)}),
            SampleRegistry
        )
