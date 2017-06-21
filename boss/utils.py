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
    try:
        return getattr(module, func_name)
    except AttributeError:
        raise ImportError("No function named {}".format(func_name))


def iterate_subclasses(klass_map, target_klass):
    for name, value in klass_map.items():
        try:
            klass_is_subclass = class_is_subclass(value, target_klass)
        except TypeError:
            pass
        else:
            if klass_is_subclass:
                yield value


def class_is_subclass(value, target_klass):
    return issubclass(value, target_klass) and value is not target_klass


def get_class_from_type_value(type_name, target_klass, conf, config, klass_map):
    valid_klasses = []
    klass_type = conf['type']
    for klass in iterate_subclasses(klass_map, target_klass):
        valid_klasses.append(klass.NAME)
        if klass.NAME == klass_type:
            return klass.from_configs(config, conf)

    if ':' in klass_type:
        klass = import_function(klass_type)
        if class_is_subclass(klass, target_klass):
            return klass.from_configs(config, conf)

    raise ValueError(
        "unknown {} type {!r}.\n"
        "valid types: {}".format(
            type_name,
            klass_type,
            valid_klasses
        )
    )


class request_maker(object):
    def __init__(self, target):
        self.target = target

    def __call__(self, params):
        requests.post(self.target, data=json.dumps(params))
