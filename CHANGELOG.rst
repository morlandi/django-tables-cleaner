.. :changelog:

History
=======

v0.1.4
------
* Example project added
* Refactoring: app logic moved to standalone Python functions
* Unit tests added

v0.1.3
------
* Python and Django classifiers added to setup.py

v0.1.2
------
* apply vacuum only when supported by db engines

v0.1.1
------
* published on PyPI

v0.1.0
------
* prepare for publishing on PyPI
* use "VACUUM" instead of "VACUUM FULL"
* dry run option renamed as "-d" (was "-n")

v0.0.5
------
* Fix for Django 2.x: call super() from Command.__init__() as required

v0.0.4
------
* Customizable 'get_latest_by' attribute
* Remove EmptyResultSet import which is not available in older versions of Django

v0.0.3
------
* Setup fix

v0.0.2
------
* First working implementation

v0.0.1
------
* Initial setup
