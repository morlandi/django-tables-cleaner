import logging
import sys
import signal
from django.db import transaction
from django.db import connections
from django.db import DEFAULT_DB_ALIAS

from tables_cleaner import clean_tables

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

            clean_tables(logger=self.logger, dry_run=self.dry_run)

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
