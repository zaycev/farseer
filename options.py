# -*- coding: utf-8 -*-import sysimport loggingimport datetimetm = datetime.datetime.now()LOG_CONF = {	"level": logging.DEBUG,#	"filename": "/home/infolab/www/public/logs/farseerv01_log_{0}.l"\#				"og.txt".format(tm.strftime("%Y.%m.%d_%H-%M-%S")),}logging.basicConfig(**LOG_CONF)sys.tracebacklimit = 128DATABASE_CONFIG = {	"pg": {		"driver": "django.db.backends.postgresql_psycopg2",		"host": "192.168.1.7",		"port": "5432",		"database": "farseer-db",		"user": "farseer",		"password": "zM7$bl:zYPqj$ak+",	},	"redis": {		"host": "192.168.1.7",		"port": 6379,		"db": 1,	}}