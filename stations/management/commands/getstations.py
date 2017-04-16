import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry

import logger

from stations.models import Stations as Station
import stations.management.commands.utils as utils


LOG = logger.FilePrintLogger(__name__)


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
            LOG.set_file_handler(log_path, logging.INFO)

        LOG.info('Getting stations...')
        counter = 0
        count_created = 0
        time_start = utils.start_timer()
        stations = utils.get_river_stations(
            with_typical_range=options['with_typical_range'], parameter='level',
            qualifier='Stage', limit=10000)
        for s in stations:
            sdict = s._asdict()
            stn_ref = sdict.pop('station_ref')
            stn_pt = sdict.pop('point')

            stn, created = Station.objects.update_or_create(station_ref=stn_ref,
                point=GEOSGeometry('POINT ({} {})'.format(*stn_pt)),
                defaults=sdict)
            if created:
                count_created += 1
            counter += 1
            stn.save()
        time_diff = utils.end_timer(time_start)
        LOG.info('Loaded {} new station(s) of {} in {}'.format(
            count_created, counter, time_diff))
