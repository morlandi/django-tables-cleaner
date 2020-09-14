from datetime import timedelta
import traceback
from django.apps import apps
from django.utils import timezone
from .app_settings import TABLES


def clean_tables(logger=None, dry_run=False):

    for table in TABLES:

        model_name = table.get('model_name', None)

        # Support 'model' instead of 'model_name' for backward compatibility;
        # To be deprecated
        if model_name is None and 'model' in table:
            model_name = table.get('model', None)
            table.pop('model')
            table['model_name'] = model_name

        try:
            if logger is not None:
                logger.info('Cleaning table "%s"' % model_name)
            n = clean_table(**table, logger=logger, dry_run=dry_run)
            if logger:
                if dry_run:
                    logger.info('DRY-RUN: %d records would be removed from "%s"' % (n, model_name))
                else:
                    logger.info('%d records removed from "%s"' % (n, model_name))
        except Exception as e:
            if logger:
                logger.error(str(e))
                logger.debug(traceback.format_exc())


def clean_table(model_name, keep_records, keep_since_days, keep_since_hours, get_latest_by=None, logger=None, dry_run=False):

    def dump_queryset(queryset, get_latest_by):
        first = queryset.first()
        try:
            last = queryset.last()
        except TypeError as e:
            if logger is not None:
                logger.info(str(e))
                logger.debug(traceback.format_exc())
            # TypeError('Cannot reverse a query once a slice has been taken.')
            n = len(queryset)
            last = queryset[n - 1] if n > 0 else None

        return 'records: %d [%s ... %s]' % (
            queryset.count(),
            getattr(first, get_latest_by).isoformat() if first is not None else '',
            getattr(last, get_latest_by).isoformat() if last is not None else '',
        )

    # Retrieve model
    model = apps.get_model(model_name)

    # Retrieve get_latest_by for model
    if get_latest_by is None:
        get_latest_by = getattr(model._meta, 'get_latest_by', None)
    #get_latest_by = getattr(model._meta, 'get_latest_by', None)
    if get_latest_by is None:
        raise Exception('"%s": missing required attribute "get_latest_by"' % model_name)
    if get_latest_by.startswith('-'):
        get_latest_by = get_latest_by[1:]

    # Prepare a queryset of all records to be deleted
    queryset = model.objects.order_by(get_latest_by)
    table_size = queryset.count()
    if logger is not None:
        logger.debug('"%s": records count before cleaning: %d' % (model_name, table_size))

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

    if logger is not None:
        try:
            logger.debug('sql: ' + str(queryset.query))
        #except EmptyResultSet:
        except Exception as e:
            logger.debug("sql: %s" % str(e))

        logger.debug('"%s": records to keep: %d' % (model_name, table_size - queryset.count()))
        logger.debug('"%s": records to be removed: %d' % (model_name, queryset.count()))
        logger.debug(dump_queryset(queryset, get_latest_by))
    n = queryset.count()

    if not dry_run:
        for row in queryset.iterator():
            row.delete()

    return n
