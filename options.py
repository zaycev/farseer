# -*- coding: utf-8 -*-import sysimport loggingLOG_CONF = {	"level": logging.DEBUG,#	"file": "/home/infolab/www/public/logs/farseer-last.txt"}logging.basicConfig(**LOG_CONF)sys.tracebacklimit = 128DATABASE_CONFIG = {	"pg": {		"driver": "django.db.backends.postgresql_psycopg2",		"host": "192.168.1.4",		"port": "5432",		"database": "farseer-db",		"user": "farseer",		"password": "zM7$bl:zYPqj$ak+",	},	"redis": {		"host": "192.168.1.4",		"port": 6379,		"db": 1,	}}