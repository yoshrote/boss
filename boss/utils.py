import importlib
import json
from datetime import datetime, timedelta, time

import requests


DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def parse_timedelta(delta):
    hours, minutes, seconds = map(int, delta.split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

def parse_datetime(dt_stamp):
    return datetime.strptime(dt_stamp, '%Y-%m-%dT%H:%M:%SZ')

def parse_time(t_stamp):
    hour, minute, second = map(int, t_stamp.split(':'))
    return time(hour, minute, second)

def stringify_datetime(dt_stamp):
    return dt_stamp.strftime('%Y-%m-%dT%H:%M:%SZ')

def import_function(func):
    name, _, func_name = func.partition(':')
    module = importlib.import_module(name)
    return getattr(module, func_name)


class request_maker(object):
    def __init__(self, target):
        self.target = target

    def __call__(self, params):
        requests.post(self.target, data=json.dumps(params))
