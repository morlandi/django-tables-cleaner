import logging
import sys
import signal
import traceback
from django.apps import apps
from django.db import transaction
from django.db import connections
from django.db import DEFAULT_DB_ALIAS
from datetime import timedelta
from django.utils import timezone
#from django.core.exceptions import EmptyResultSet

from tables_cleaner.app_settings import TABLES

from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


def signal_handler(signal, frame):
    sys.exit(0)


class Command(BaseCommand):

    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger or logging.getLogger(__name__)
        signal.signal(signal.SIGINT, signal_handler)

    def add_arguments(self, parser):
        parser.add_argument(
            '--database', action='store', dest='database', default=DEFAULT_DB_ALIAS,
            help='Nominates a specific database to load fixtures into. Defaults to the "default" database.',
        )
        parser.add_argument('-d', '--dry-run', action='store_true', default=False, help="Don't actually delete records (default: False)")
        parser.add_argument('--vacuum', action='store_true', default=False, help="Run VACUUM after deletion")

    def set_logger(self, verbosity):
        """
        Set logger level based on verbosity option
        """
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(module)s| %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if verbosity == 0:
            self.logger.setLevel(logging.WARN)
        elif verbosity == 1:  # default
            self.logger.setLevel(logging.INFO)
        elif verbosity > 1:
            self.logger.setLevel(logging.DEBUG)

        # verbosity 3: also enable all logging statements that reach the root logger
        if verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)

    def handle(self, *args, **options):
        self.set_logger(options.get('verbosity'))
        self.using = options['database']
        self.dry_run = options['dry_run']
        self.vacuum = options['vacuum']

        self.logger.info("***** clean_tables started on db %s. *****" % self.using)

        # Be transactional !
        with transaction.atomic(using=self.using):

            for table in TABLES:
                try:
                    self.logger.info('Cleaning table "%s"' % table['model'])
                    n = self.clean_table(table)
                    if self.dry_run:
                        self.logger.info('DRY-RUN: %d records would be removed from "%s"' % (n, table['model']))
                    else:
                        self.logger.info('%d records removed from "%s"' % (n, table['model']))
                except Exception as e:
                    self.logger.error(str(e))
                    self.logger.debug(traceback.format_exc())

            # Close the DB connection -- unless we're still in a transaction. This
            # is required as a workaround for an edge case in MySQL: if the same
            # connection is used to create tables, load data, and query, the query
            # can return incorrect results. See Django #7572, MySQL #37735.
            if transaction.get_autocommit(self.using):
                connections[self.using].close()

        if self.vacuum and not self.dry_run:
            self.vacuum_db(connections[self.using])

        self.logger.info("*** clean_tables done.")

    def vacuum_supported(self, connection):
        supported_engines = [
            'postgresql',
            'postgis',
            'sqlite',
            'spatialite',
        ]
        engine_module = connection.__class__.__module__
        for engine in supported_engines:
            if engine in engine_module:
                return True
        self.logger.warn('Vacuum not supported on %s' % engine_module)
        return False

    def vacuum_db(self, connection):
        if not self.vacuum_supported(connection):
            self.logger.warn('VACUUM skipped')
            return False
        self.logger.info('Executing VACUUM')
        cursor = connection.cursor()
        cursor.execute('VACUUM')
        cursor.close()
        return True

    def clean_table(self, table):

        def dump_queryset(queryset, get_latest_by):
            first = queryset.first()
            try:
                last = queryset.last()
            except TypeError as e:
                self.logger.info(str(e))
                self.logger.debug(traceback.format_exc())
                # TypeError('Cannot reverse a query once a slice has been taken.')
                n = len(queryset)
                last = queryset[n - 1] if n > 0 else None

            return 'records: %d [%s ... %s]' % (
                queryset.count(),
                getattr(first, get_latest_by).isoformat() if first is not None else '',
                getattr(last, get_latest_by).isoformat() if last is not None else '',
            )

        # Retrieve model
        model = apps.get_model(table['model'])

        # Retrieve get_latest_by for model
        get_latest_by = table.get('get_latest_by', getattr(model._meta, 'get_latest_by', None))
        #get_latest_by = getattr(model._meta, 'get_latest_by', None)
        if get_latest_by is None:
            raise Exception('"%s": missing required attribute "get_latest_by"' % table['model'])
        if get_latest_by.startswith('-'):
            get_latest_by = get_latest_by[1:]

        # Settings for this table
        keep_records = table.get('keep_records', 0)
        keep_since_days = table.get('keep_since_days', 0)
        keep_since_hours = table.get('keep_since_hours', 0)

        # Prepare a queryset of all records to be deleted
        queryset = model.objects.order_by(get_latest_by)
        table_size = queryset.count()
        self.logger.debug('"%s": records count before cleaning: %d' % (table['model'], table_size))

        # Filter queryset to preserve most recent records
        if keep_since_hours > 0:
            time_threshold = timezone.now() - timedelta(hours=keep_since_hours)
            queryset = queryset.filter(**{get_latest_by + '__lt': time_threshold})
        if keep_since_days > 0:
            time_threshold = timezone.now() - timedelta(days=keep_since_days)
            queryset = queryset.filter(**{get_latest_by + '__lt': time_threshold})

        # Reduce the queryset to preserve at least 'keep_records' records
        records_left = table_size - queryset.count()
        if keep_records > 0 and records_left < keep_records:
            records_to_remove = max(queryset.count() - (keep_records - records_left), 0)
            queryset = queryset[0:records_to_remove]

        try:
            self.logger.debug('sql: ' + str(queryset.query))
        #except EmptyResultSet:
        except Exception as e:
            self.logger.debug("sql: %s" % str(e))

        self.logger.debug('"%s": records to keep: %d' % (table['model'], table_size - queryset.count()))
        self.logger.debug('"%s": records to be removed: %d' % (table['model'], queryset.count()))
        #self.logger.debug(dump_queryset(queryset, get_latest_by))
        n = queryset.count()

        if not self.dry_run:
            self.delete_records(queryset)

        return n

    def delete_records(self, queryset):
        for row in queryset.iterator():
            row.delete()
