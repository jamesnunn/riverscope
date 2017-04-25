from datetime import datetime, timedelta, timezone
import logging
import os
from multiprocessing.pool import ThreadPool

from django.core.management.base import BaseCommand
from django.db import transaction

import logger

from stations.models import Stations, StationReadings
import stations.management.commands.utils as utils


LOG = logger.FilePrintLogger(__name__)


def get_readings(station):
    url = utils.readings_url(measure=station.measure, sort=True, limit=10)
    station_readings = []
    try:
        measures = utils.get_url_json_response(url)
        for measure in measures['items']:
            date = datetime.strptime(measure['dateTime'], '%Y-%m-%dT%H:%M:%SZ')
            date = date.replace(tzinfo=timezone.utc)
            value = float(measure['value'])
            station_readings.append(StationReadings(station=station, datetime=date, measure=value))
            # StationReadings.objects.create(station=station, datetime=date, measure=value)
        return station_readings
    except Exception as err:
        LOG.warning('Skipped reading for {}: {}'.format(station.station_ref, str(err)))


class Command(BaseCommand):
    help = 'Get latest readings for stations.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--lastn', type=int, default=10,
                            help='Get last n readings.')
        parser.add_argument('-d', '--debug', action='store_true',
                            help='Run in debug mode')
        parser.add_argument('-l', '--log', help='Set the log directory',
                            default=os.path.join(os.path.expanduser('~')),
                            metavar='path')

    def handle(self, *args, **options):
        # Setup logger with levels and path
        log_path = os.path.join(options['log'], 'riverscope', __name__ + '_log.txt')
        if options['debug']:
            LOG.set_print_handler_level(logging.DEBUG)
            LOG.set_file_handler(log_path, logging.DEBUG)
        else:
            LOG.set_print_handler_level(logging.INFO)
            LOG.set_file_handler(log_path, logging.DEBUG)

        time_start = utils.start_timer()
        pool = ThreadPool(100)
        # TODO http://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
        results = list(filter(None, pool.map(get_readings, Stations.objects.all())))
        station_readings = [s for sl in results for s in sl]
        with transaction.atomic():
            StationReadings.objects.all().delete()
            StationReadings.objects.bulk_create(station_readings)
        time_diff = utils.end_timer(time_start)
        LOG.info('Added {} readings in {}'.format(len(station_readings), time_diff))
