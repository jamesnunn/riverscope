import logging
import os
import sys
from multiprocessing.pool import ThreadPool

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry
from django.db.utils import OperationalError

import logger

from django.core.exceptions import ObjectDoesNotExist
from stations.models import Stations
import stations.management.commands.utils as utils


LOG = logger.FilePrintLogger(__name__)


def add_station(station):
    count_created = 0
    count_updated = 0
    stn_dict = dict(station._asdict())
    # pop out these variables as we will use them separately
    stn_ref = stn_dict.pop('station_ref')
    stn_pt = stn_dict.pop('point')
    stage_scale_url = stn_dict['stage_scale_url']
    if stage_scale_url:
        stage_scale = utils.get_url_json_response(stage_scale_url)
        typical_low = float(stage_scale['items']['typicalRangeLow'])
        typical_high = float(stage_scale['items']['typicalRangeHigh'])
        stn_dict['typical_low'] = typical_low
        stn_dict['typical_high'] = typical_high
    # Only add if doesn't exist, update if it does.
    try:
        exist_stn = Stations.objects.get(station_ref=stn_ref)
        exist_stn_dict = {k: v for k, v in exist_stn.__dict__.items() if k in stn_dict}
        # get the new attributes to check if it has been updated
        updated = exist_stn_dict != stn_dict
    except ObjectDoesNotExist:
        exist_stn = None
        updated = False

    try:
        obj, created = Stations.objects.update_or_create(
            station_ref=stn_ref,
            point=GEOSGeometry('POINT ({} {})'.format(*stn_pt)),
            defaults=stn_dict)
    except OperationalError as err:
        LOG.error('ERROR: ' + ' '.join((str(err).split())))
        sys.exit(1)

    # only save if there are changes, to reduce writes
    if created:
        obj.save()
        count_created += 1

    if updated:
        count_updated += 1

    return count_created, count_updated


class Command(BaseCommand):
    help = 'Updates all gauge stations from the EA.'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--with_typical_range', action='store_true',
                            default=False, help='Also cache typical range. '
                            'WARNING this takes some time.')
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
        found_stations = utils.get_river_stations(
            with_typical_range=options['with_typical_range'], parameter='level',
            qualifier='Stage', limit=10000)
        pool = ThreadPool(100)
        results = pool.map(add_station, found_stations)
        count_created, count_updated = map(sum, zip(results))
        time_diff = utils.end_timer(time_start)
        LOG.info('Added {}, updated {} stations of {} in {}'.format(
            count_created, count_updated, len(found_stations), time_diff))
