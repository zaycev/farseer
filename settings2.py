# -*- coding: utf-8 -*-
import logging

ORM_CONFIG = {
	"DB_DRIVER": "postgresql+psycopg2",
	"DB_USER": "farseer",
	"DB_PASSWORD": "farseer",
	"DB_HOST": "localhost",
	"DB_PORT": "5432",
	"DB_DATABASE": "bi-1",
}

LOG_CONF = {
	"level": logging.DEBUG,
	"filename": "/Volumes/HFS/logs/last.txt",
	"filemode": "w",
}