import unittest
from datetime import datetime, timedelta, time

import mock

from boss.config import Configurator
from boss.interfaces import Scheduler
from boss.schedules import pick_schedule, RunEvery, RunAt
from boss.utils import stringify_datetime, DT_FORMAT


class SampleScheduler(Scheduler):
    @classmethod
    def from_config(cls, config, schedule_config):
        return cls()

    def should_run(self, state):
        return False


class SchedulerTests(unittest.TestCase):
    def test_pick_schedule(self):
        mock_config = mock.Mock(autospec=Configurator)

        self.assertIsInstance(pick_schedule(mock_config, {'type': 'run at', 'target_time': '00:05:00'}), RunAt)
        self.assertIsInstance(pick_schedule(mock_config, {'type': 'run every', 'frequency': '00:05:00'}), RunEvery)
        self.assertIsInstance(pick_schedule(mock_config, {'type': '{}:SampleScheduler'.format(__name__)}), SampleScheduler)
        self.assertRaises(ValueError, pick_schedule, mock_config, {'type': 'datetime:datetime'})
        self.assertRaises(ValueError, pick_schedule, mock_config, {'type': 'scheduler.that.does.not:exist'})

    def test_run_every(self):
        freq = timedelta(minutes=5)
        now = datetime(2017, 5, 23)

        schedule = RunEvery(freq)
        schedule.now = lambda: now

        # initial run
        self.assertTrue(schedule.should_run({}))
        # last run just happened
        self.assertFalse(schedule.should_run({'last_run': stringify_datetime(now)}))
        # last run IN THE FUTURE!
        self.assertFalse(schedule.should_run({'last_run': stringify_datetime(now + freq)}))
        # last run at edge of frequency
        self.assertTrue(schedule.should_run({'last_run': stringify_datetime(now - freq)}))
        # last run was a while ago
        self.assertTrue(schedule.should_run({'last_run': stringify_datetime(now - freq - freq)}))

    def test_run_at(self):
        grace = timedelta(minutes=5)
        half_grace = grace / 2

        now = datetime(2017, 5, 23, 0, 0, 0)

        schedule = RunAt(time(hour=0, minute=0, second=0), grace)

        # initial run outside of grace
        schedule.now = lambda: now - grace
        self.assertFalse(schedule.should_run({}))
        schedule.now = lambda: now + grace
        self.assertFalse(schedule.should_run({}))

        # initial run inside of grace
        schedule.now = lambda: now
        self.assertTrue(schedule.should_run({}))
        schedule.now = lambda: now + half_grace
        self.assertTrue(schedule.should_run({}))

        # last run inside grace; now inside grace
        state = {'last_run': now.strftime(DT_FORMAT)}
        schedule.now = lambda: now + half_grace
        self.assertFalse(schedule.should_run(state))

        # last run inside grace; now outside grace
        state = {'last_run': now.strftime(DT_FORMAT)}
        schedule.now = lambda: now + grace * 2
        self.assertFalse(schedule.should_run(state))

        # last run outside grace; now inside grace
        state = {'last_run': (now - grace * 2).strftime(DT_FORMAT)}
        schedule.now = lambda: now
        self.assertTrue(schedule.should_run(state))

        # last run outside grace; now outside grace
        state = {'last_run': (now - grace * 2).strftime(DT_FORMAT)}
        schedule.now = lambda: now - grace * 2
        self.assertFalse(schedule.should_run(state))
