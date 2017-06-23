import unittest
from datetime import datetime, timedelta, time

import mock

from boss.config import Configurator
from boss.interfaces import Scheduler
from boss.schedules import pick_schedule, RunEvery, RunAt
from boss.utils import stringify_datetime


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
        now = datetime(2017, 5, 23, 0, 0, 0)

        schedule = RunAt(time(hour=0, minute=0, second=0), grace)

        # initial run outside of grace
        schedule.now = lambda: now - grace - grace
        self.assertTrue(schedule.should_run({}))
        # initial run inside of grace
        schedule.now = lambda: now
        self.assertTrue(schedule.should_run({}))
        schedule.now = lambda: now + grace
        self.assertTrue(schedule.should_run({}))

        # last run inside grace; now inside grace
        # last run inside grace; now outside grace
        # last run outside grace; now inside grace
        # last run outside grace; now outside grace
'''
    def should_run(self, state):
        now = self.now()
        last_run = parse_datetime(state.get('last_run', self.DEFAULT_LAST_RUN))
        target_time = datetime.combine(now.date(), self.target_time)

        grace_period = target_time + self.grace

        LOG.debug("now_within_grace = %r <= %r < %r", target_time, now, grace_period)
        now_within_grace = target_time <= now < grace_period
        if not last_run:
            return now_within_grace

        LOG.debug("last_run_within_grace = %r <= %r < %r", target_time, last_run, grace_period)
        last_run_within_grace = target_time <= last_run < grace_period
        return now_within_grace and not last_run_within_grace
'''
