# -*- coding: utf-8 -*-from handler import CollectorHandlerimport loggingimport datetimetm = datetime.datetime.now()DATABASE_CONFIG = {	"repository": {		"driver": "postgresql+psycopg2",		"host": "localhost",		"port": "5432",		"database": "repository-P20120220",		"user": "farseer",		"password": "zM7$bl:zYPqj$ak+",	},	"arxiv": {		"driver": "postgresql+psycopg2",		"host": "localhost",		"port": "5432",		"database": "arxiv",		"user": "farseer",		"password": "zM7$bl:zYPqj$ak+",	},	"web": {		"driver": "django.db.backends.postgresql_psycopg2",		"host": "localhost",		"port": "5432",		"database": "farseer-db",		"user": "farseer",		"password": "zM7$bl:zYPqj$ak+",	},	"redis": {		"host": "localhost",		"port": 6379,		"db": 0,		"flushsb": True,		"timeout": 5,		"queue_size": 512,	}}#LOG_CONF = {#	"level": logging.DEBUG,##	"filename":     "/home/infolab/www/public/logs/farseer_log_{0}.log.txt".format(tm.strftime("%Y.%m.%d_%H-%M-%S")),##	"filename":	"/Volumes/ZFS 1Tb/logs/farseer_{0}.txt".format(tm.strftime("%Y.%m.%d_%H-%M-%S")),##	"filemode":	"w",#}##WORKFLOW = [#	CollectorHandler(wk="bi.worker.river_uri_former", size=1),#	CollectorHandler(wk="bi.worker.river_fetcher", persistent="sys.worker.sql_writer", size=16),#	CollectorHandler(wk="bi.worker.river_parser", size=3),#	CollectorHandler(wk="bi.worker.topic_fetcher", persistent="sys.worker.sql_writer", size=64),##	CollectorHandler(wk="bi.worker.topic_parser", size=5),##	CollectorHandler(wk="sn.worker.sn_fetcher", persistent="sys.worker.sql_writer", size=16),#]##BOOTSTRAP = ("bi.task.river_range", {"f":2600, "t":7500},)