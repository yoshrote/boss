import mock
import unittest

from boss.schedules import (
    RunAt,
    RunEvery
)
from boss.utils import parse_time, request_maker
from boss.task import Task


class TestTask(unittest.TestCase):
    def test_local_task(self):
        config = object()
        task_config = {
            "name": "test_task",
            "scope": "test_scope",
            "schedule": {
                "type": "run at",
                "target_time": "00:00:00"
            },
            "function": {
                "type": "local",
                "target": "boss.utils:parse_time"
            }
        }
        task = Task(config, task_config)
        self.assertEquals(task.name, task_config["name"])
        self.assertEquals(task.scope, task_config["scope"])
        self.assertIsInstance(task.scheduler, RunAt)
        self.assertIs(task.func, parse_time)
        with mock.patch.object(task, "func") as mock_func:
            params = object()
            task.run(params)
            mock_func.assert_called_once_with(params)

    def test_remote_task(self):
        config = object()
        task_config = {
            "name": "test_task",
            "scope": "test_scope",
            "schedule": {
                "type": "run every",
                "frequency": "00:05:00"
            },
            "function": {
                "type": "remote",
                "target": "https://postman-echo.com/post"
            }
        }
        task = Task(config, task_config)
        self.assertEquals(task.name, task_config["name"])
        self.assertEquals(task.scope, task_config["scope"])
        self.assertIsInstance(task.scheduler, RunEvery)
        self.assertIsInstance(task.func, request_maker)
        with mock.patch.object(task, "func") as mock_func:
            params = object()
            task.run(params)
            mock_func.assert_called_once_with(params)

    def test_unknown_task(self):
        config = object()
        task_config = {
            "name": "test_task",
            "scope": "test_scope",
            "schedule": {
                "type": "run every",
                "frequency": "00:05:00"
            },
            "function": {
                "type": "unknown task",
            }
        }
        self.assertRaises(ValueError, Task, config, task_config)
