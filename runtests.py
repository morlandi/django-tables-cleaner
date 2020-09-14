#!/usr/bin/env python
import os
import sys

# See "Using the Django test runner to test reusable applications":
# https://docs.djangoproject.com/en/3.1/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))
