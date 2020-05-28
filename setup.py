import os
import re
from setuptools import find_packages, setup


def get_version(*file_paths):
    """Retrieves the version from django_task/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

version = get_version("tables_cleaner", "__init__.py")
readme = open('README.rst').read()
history = open('CHANGELOG.rst').read().replace('.. :changelog:', '')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tables-cleaner',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A Django app used to remove oldest records from specific db tables.',
    long_description=readme + '\n\n' + history,
    url='https://github.com/morlandi/django-tables-cleaner',
    author='Mario Orlandi',
    author_email='morlandi@brainstorm.it',
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
