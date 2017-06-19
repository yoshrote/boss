import argparse
import logging

from boss.app import Application
from boss.config import Configurator
from boss.task import Task

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Make requests on a schedule.')
parser.add_argument('config', metavar='CONFIG_FILE',
                    help='the path to the configuration file')

args = parser.parse_args()
logger.info('Using config file: %s', args.config)
config = Configurator.from_file(args.config)


class MyApp(Application):
    Task = Task


def heartbeat(params):
    pass


def echo(params):
    print params


app = MyApp(config, config.registry)
app.run()
