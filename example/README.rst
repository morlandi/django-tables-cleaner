
Install
=======

Create a virtualenv, then ...

Install Django dependencies:

.. code-block:: bash

    pip install -r requirements.txt

Initialize database tables:

.. code-block:: bash

    python manage.py migrate

Create a super-user for the admin:

.. code-block:: bash

    python manage.py createsuperuser

Run
===

.. code-block:: bash

    python manage.py runserver

Visit http://127.0.0.1:8000/ and follow instructions::

    You can populate the Sample table manually or using the management command create_samples.
    Then, run the management command clean_tables and see what happens ...

    Also, try different values for TABLES_CLEANER_TABLES in project's settings.
