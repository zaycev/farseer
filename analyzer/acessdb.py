# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

db_engine = None
db_session = None

def make_environment(db_config):
	db_url = URL(
		db_config["driver"],
		username=db_config["user"],
		password=db_config["password"],
		host=db_config["host"],
		port=db_config["port"],
		database=db_config["database"],)
	db_engine = create_engine(db_url, pool_size=768, max_overflow=192)
	db_session = sessionmaker(bind=db_engine, autoflush=False)()
	return db_engine, db_session