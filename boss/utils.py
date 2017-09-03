import importlib
import logging
import pkg_resources
from datetime import datetime, timedelta, time

import requests

DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
LOG = logging.getLogger(__name__)


def parse_timedelta(delta):
    hours, minutes, seconds = map(int, delta.split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def parse_datetime(dt_stamp):
    return datetime.strptime(dt_stamp, DT_FORMAT)


def parse_time(t_stamp):
    hour, minute, second = map(int, t_stamp.split(':'))
    return time(hour, minute, second)


def stringify_datetime(dt_stamp):
    return dt_stamp.strftime(DT_FORMAT)


def import_function(func):
    LOG.debug("finding function %s", func)
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
                yield name, value


def class_is_subclass(value, target_klass):
    return issubclass(value, target_klass) and value is not target_klass


def get_class_from_type_value(type_name, target_klass, conf, config):
    klass_map = {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points(
            "boss_{}".format(type_name)
        )
        if class_is_subclass(entry_point.load(), target_klass)
    }

    klass_type = conf['type']
    try:
        klass = klass_map[klass_type]
    except (KeyError, ValueError):
        raise ValueError(
            "unknown {} type {!r}.\n"
            "valid types: {}".format(
                type_name,
                klass_type,
                klass_map.keys()
            )
        )
    else:
        return klass.from_configs(config, conf)


class request_maker(object):
    def __init__(self, target):
        self.target = target

    def __call__(self, params):
        response = requests.post(self.target, json=params)
        LOG.info("%s [%s]", self.target, response.status_code)
        LOG.debug(response.content)
