=====================
django-tables-cleaner
=====================

`tables_cleaner` is a Django app which can remove (and optionally archive)
oldest records from specific db tables.

Quick start
-----------

1. Add "tables_cleaner" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'tables_cleaner',
    ]

2. Run the management command periodically::

    python manage.py clean_tables
