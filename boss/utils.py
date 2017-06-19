import importlib
import json

import requests


def import_function(func):
    name, _, func_name = func.partition(':')
    module = importlib.import_module(name)
    return getattr(module, func_name)


class request_maker(object):
    def __init__(self, target):
        self.target = target

    def __call__(self, params):
        requests.post(self.target, data=json.dumps(params))
