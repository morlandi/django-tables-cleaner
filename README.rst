=====================
django-tables-cleaner
=====================

`tables_cleaner` is a Django app used to remove oldest records from specific db tables.

It is intended to be used in production to keep under control the size of growing
tables containing temporary data (used for logging, auditing, ...), but preserving
the most recent records according to the constraints assigned by design (see `TABLES_CLEANER_TABLES` setting).

Quick start
-----------

1. Installation::

    pip install django-tables-cleaner

    or

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

The first option is to **recall periodically the management command** `clean_tables`, for example via cron:

::

    usage: manage.py clean_tables [-h] [--database DATABASE] [-d] [--vacuum]
                                  [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                                  [--pythonpath PYTHONPATH] [--traceback]
                                  [--no-color]

    optional arguments:
      -h, --help            show this help message and exit
      --database DATABASE   Nominates a specific database to load fixtures into.
                            Defaults to the "default" database.
      -d, --dry-run         Don't actually delete records (default: False)
      --vacuum              Run VACUUM after deletion
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


Or, when using a different scheduling strategy (for example with `django-cron <https://pypi.org/project/django-cron/>`_)
**you can call from Python code the following function**:

.. code :: python

    clean_tables(logger=None, dry_run=False)

For example:

.. code:: python

    import tables_cleaner
    tables_cleaner.clean_tables()


Finally, for very specific needs, you can **recall the real workhorse directly**:

.. code:: python

  def clean_table(model_name, keep_records, keep_since_days, keep_since_hours, get_latest_by=None, logger=None, dry_run=False)

which act on a single table, and doesn't require any setting.


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
            'model_name': 'backend.log',
            'keep_records': 1000,
            'keep_since_days': 1,
            'keep_since_hours': 0,
        }, {
            'model_name': 'tasks.updatedevicetask',
            'keep_records': 100,
            'keep_since_days': 0,
            'keep_since_hours': 12,
            'get_latest_by': 'created',
        },
    ]


**get_latest_by** attribute is optional; if not supplied, Model's Meta get_latest_by
is used instead.


Vacuum strategy
---------------

"VACUUM" is optionally executed as a final activity ('--vacuum').

Since version v0.1.0, we opted to use "VACUUM" instead of "VACUUM FULL", since that
seems more appropriate for ordinary database maintenance, for the following reasons:

- it's available for Postgresql and Sqlite (and, hopefully, for other databases too)
- database owners are allowed to vacuum all tables in their databases
- an exclusive lock is not required
- it's potentially much faster

PostgreSQL documentation explicitly states that `The FULL option is not recommended for routine use`;
see: `VACUUM — garbage-collect and optionally analyze a database <https://www.postgresql.org/docs/11/sql-vacuum.html>`_

Thanks to John Vandenberg for bringing my attention to this.


FileFields and ImageFields
--------------------------

Removing rows in the database when the Model contains one or more FileField or
ImageField is not enough, since some garbage is left in the Media folder.

I normally use `django-cleanup <https://pypi.org/project/django-cleanup/>`_ to cope with this.


Does it work?
-------------

A few unit tests have been provided.

Prepare the virtual environment as follows::

    python -m pip install -r requirements.txt

then::

    ./runtests.py

or::

    coverage run --source='.' runtests.py
    coverage report


References
----------

- `Using the Django test runner to test reusable applications <https://docs.djangoproject.com/en/3.1/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications>`_
- `Advanced tutorial: How to write reusable apps <https://docs.djangoproject.com/en/3.1/intro/reusable-apps/>`_
- `TODO: Running tests using tox <https://docs.djangoproject.com/en/3.1/internals/contributing/writing-code/unit-tests/#running-tests-using-tox>`_


License
-------

This code is distributed under the terms of the MIT license.
