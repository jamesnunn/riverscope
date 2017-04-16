import argparse
import logging
import os
# Make the program interruptible (e.g. keyboard Ctrl+C)
from signal import signal
from signal import SIGINT
from signal import SIG_DFL
signal(SIGINT, SIG_DFL)
import sys

import redis
import logger

from riverscope.utils import utils
from riverscope._version import __app_name__, __version__

LOG = logger.FilePrintLogger('cache_stations')

def handle_exception(exc_type, exc_value, exc_traceback):
    """An alternative exception handler

    Overrides sys.excepthook to enable logging any unhandled exception. Doesn't
    raise an exception when receiving a KeyboardInterrupt (Ctrl+C). Also logs
    and displays (if possible) a dialog displaying any unhandled exceptions.
    """
    # Pack the exception into a tuple to pass around and unpack
    exc_tuple = (exc_type, exc_value, exc_traceback)
    # Don't count Ctrl+C as an unhandled exception
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(*exc_tuple)
        return
    LOG.error('UNHANDLED EXCEPTION', exc_info=exc_tuple)
# Override sys.excepthook
sys.excepthook = handle_exception


def cache_stations():
    parser = argparse.ArgumentParser('cache_stations')
    parser.add_argument('-H', '--host', default='localhost',
                        help='Redis host to cache to.')
    parser.add_argument('-r', '--with_typical_range', action='store_true',
                        default=False, help='Also cache typical range. '
                        'WARNING this takes some time.')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Show version then exit')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('-l', '--log', help='Set the log directory',
                        default=os.path.join(os.path.expanduser('~')),
                        metavar='path')

    args = parse_args(parser)

    if args.with_typical_range:
        print('Also getting typical range. This will take several minutes.')

    time_start = utils.start_timer()
    stations = utils.get_river_stations(args.with_typical_range)
    conn_params = [args.host]
    counter = 0
    try:
        LOG.debug('Connecting to Redis on {}...'.format(', '.join(conn_params)))
        conn = redis.StrictRedis('localhost')
        for notation, station in stations:
            conn.hmset(notation, station)
            counter += 1
    except redis.exceptions.ConnectionError as err:
        LOG.error(err)
        sys.exit(1)

    time_diff = utils.end_timer(time_start)
    LOG.info('Loaded {} stations in {}'.format(counter, time_diff))


def parse_args(parser):
    args, unknown_args = parser.parse_known_args()
    # If we have unknown args, let the user know, then exit
    if unknown_args:
        for arg in unknown_args:
            print('option {arg} not recognised'.format(arg=arg))
        parser.print_help()
        sys.exit(1)

    # Show the program version info
    if args.version:
        print(' '.join((__app_name__, __version__)))
        sys.exit()

    # Setup logger with levels and path
    log_path = os.path.join(args.log, __app_name__, parser.prog + '_log.txt')
    if args.debug:
        LOG.set_print_handler_level(logging.DEBUG)
        LOG.set_file_handler(log_path, logging.DEBUG)
    else:
        LOG.set_print_handler_level(logging.INFO)
        LOG.set_file_handler(log_path, logging.INFO)

    return args
