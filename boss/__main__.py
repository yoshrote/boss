import argparse
import logging

from .app import Application
from .config import Configurator


logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Make requests on a schedule.')
parser.add_argument('config', metavar='CONFIG_FILE',
                    help='the path to the configuration file')

args = parser.parse_args()
logger.info('Using config file: %s', args.config)
config = Configurator.from_file(args.config)


class MyApp(Application):
    TaskFinder = config.task_finder
    Task = config.task
    ParameterFinder = config.scope_finder
    Registry = config.registry


def heartbeat(params):
    pass


def echo(params):
    print params


app = MyApp(config)
app.run()
