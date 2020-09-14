import os

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "tests",
]

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'NAME': ':memory:',
    }
}


TABLES_CLEANER_TABLES = [
    {
        'model_name': 'tests.sample',
        'keep_records': 50,
        'keep_since_days': 0,
        'keep_since_hours': 0,
        #'get_latest_by': 'created',
    },
]
