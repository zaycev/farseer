# -*- coding: utf-8 -*-from handler import CollectorHandlerimport loggingimport datetimetm = datetime.datetime.now()DATABASE_CONFIG = {	"repository": {		"driver": "postgresql+psycopg2",#		"host": "192.168.50.172",#		"host": "91.193.218.140",		"host": "localhost",		"port": "5432",		"database": "repository-P20120220",		"user": "farseer-public",		"password": "farseer",	},	"arxiv": {		"driver": "postgresql+psycopg2",#		"host": "192.168.50.172",#		"host": "91.193.218.140",		"host": "localhost",		"port": "5432",		"database": "arxiv",		"user": "farseer-public",		"password": "farseer",	},	"web": {		"driver": "django.db.backends.postgresql_psycopg2",#		"host": "192.168.50.172",#		"host": "91.193.218.140",		"host": "localhost",		"port": "5432",		"database": "web",		"user": "farseer-public",		"password": "farseer",	},	"redis": {		"host": "localhost",		"port": 6379,		"db": 0,		"flushsb": True,		"timeout": 5,		"queue_size": 512,	}}LOG_CONF = {	"level": logging.DEBUG,#	"filename":     "../../../webdav/logs/farseer_{0}.txt".format(tm.strftime("%Y.%m.%d_%H-%M-%S")),#	"filename":	"/Volumes/ZFS 1Tb/logs/farseer_{0}.txt".format(tm.strftime("%Y.%m.%d_%H-%M-%S")),#	"filemode":	"w",}WORKFLOW = [	CollectorHandler(wk="bi.worker.river_uri_former", size=1),	CollectorHandler(wk="bi.worker.river_fetcher", size=16),	CollectorHandler(wk="bi.worker.river_parser", size=3),	CollectorHandler(wk="bi.worker.topic_fetcher", size=128),	CollectorHandler(wk="bi.worker.topic_parser", size=5),	CollectorHandler(wk="sn.worker.sn_fetcher", persistent="sys.worker.sql_writer", size=16),]BOOTSTRAP = ("bi.task.river_range", {"f":2600, "t":7500},)