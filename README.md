Farseer Project
===============

Description
-----------


Contributors
------------
1. Vladimir Zaytsev [<vladimir@zvm.me>](mailto:vladimir@zvm.me)

Depencies
---------
* Python 2.7.x

* python-protobuf: [code.google.com/p/protobuf](http://code.google.com/p/protobuf/)

* python-redis: [pypi.python.org/pypi/redis](http://pypi.python.org/pypi/redis/)

* python-psycopg2: [pypi.python.org/pypi/psycopg2](http://pypi.python.org/pypi/psycopg2/)

* python-django: [djangoproject.com](https://www.djangoproject.com/)

* python-sqlalchemy: [sqlalchemy.org](www.sqlalchemy.org/)

* python-lxml: [xml.de](http://xml.de/)

Commands
--------
1. run data collector:

	`python run.py collecor`
	
2. run lexicon builder:

	`python run.py analyzer`
	
3. run feature selection :
	
	`python run.py selection`

4. run django web-ui front-end:

	`python manage.py syncdb`
	
	`python manage.py runserver <ip-address>:<port>`