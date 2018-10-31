=====================
django-tables-cleaner
=====================

`tables_cleaner` is a Django app which can remove (and optionally archive)
oldest records from specific db tables.

Quick start
-----------

1. Installation::

  pip install git+https://github.com/morlandi/django-tables-cleaner

2. Add "tables_cleaner" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'tables_cleaner',
    ]

3. Run the management command periodically (i.e. with cron) ::

    python manage.py clean_tables

Usage
-----

::

    usage: manage.py clean_tables [-h] [--database DATABASE] [-n] [--vacuum]
                                  [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                                  [--pythonpath PYTHONPATH] [--traceback]
                                  [--no-color]

    optional arguments:
      -h, --help            show this help message and exit
      --database DATABASE   Nominates a specific database to load fixtures into.
                            Defaults to the "default" database.
      -n, --dry-run         Don't actually delete records (default: False)
      --vacuum              Run VACUUM FULL after deletion (Postgresql only)
      --version             show program's version number and exit
      -v {0,1,2,3}, --verbosity {0,1,2,3}
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on CommandError exceptions
      --no-color            Don't colorize the command output.

Settings
--------

TABLES_CLEANER_TABLES
    The list of models to be cleaned;

    options:

        - keep_records: n. of most recent records to be preserved; 0=unused
        - keep_since_days: always preserve records more recent than this; 0=unused
        - keep_since_hourse: always preserve records more recent than this; 0=unused

Example::

    TABLES_CLEANER_TABLES = [
        {
            'model': 'backend.log',
            'keep_records': 1000,
            'keep_since_days': 1,
            'keep_since_hours': 0,
        }, {
            'model': 'tasks.updatedevicetask',
            'keep_records': 100,
            'keep_since_days': 0,
            'keep_since_hours': 12,
        },
    ]
