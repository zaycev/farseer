# -*- coding: utf-8 -*-
from google.protobuf.descriptor import FieldDescriptor

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy import Integer, Text, Float, Boolean, Binary

from collector.core.server.service import Worker
from collector.core.server.service import Service

PROTOBUFF_SQL_MAP = {
	FieldDescriptor.TYPE_BOOL: Boolean,
	FieldDescriptor.TYPE_BYTES: Binary,
	FieldDescriptor.TYPE_DOUBLE: Float,
	FieldDescriptor.TYPE_ENUM: None,
	FieldDescriptor.TYPE_FIXED32: None,
	FieldDescriptor.TYPE_FIXED64: None,
	FieldDescriptor.TYPE_FLOAT: Float,
	FieldDescriptor.TYPE_INT32: Integer,
	FieldDescriptor.TYPE_INT64: Integer,
	FieldDescriptor.TYPE_MESSAGE: None,
	FieldDescriptor.TYPE_SFIXED32: None,
	FieldDescriptor.TYPE_SFIXED64: None,
	FieldDescriptor.TYPE_STRING: Text,
	FieldDescriptor.TYPE_UINT32: Integer,
	FieldDescriptor.TYPE_UINT64: Integer,
}

ORM_CONFIG = {
	"DB_DRIVER": "postgresql+psycopg2",
	"DB_USER": "farseer",
	"DB_PASSWORD": "farseer",
	"DB_HOST": "localhost",
	"DB_PORT": "5432",
	"DB_DATABASE": "bi-1",
}


class TaskWriter(Worker):
	name = "worker.task_writer"

class SqlWriter(Worker):
	name = "worker.sql_writer"

	def __after_init__(self, mailbox, **kwargs):
		url = "postgresql+psycopg2://farseer:farseer@localhost/bi-1"
#		url = URL(
#			ORM_CONFIG["DB_DRIVER"],
#			username=ORM_CONFIG["DB_USER"],
#			password=ORM_CONFIG["DB_PASSWORD"],
#			host=["DB_HOST"],
#			port=ORM_CONFIG["DB_PORT"],
#			database=ORM_CONFIG["DB_DATABASE"]
#		)
		mailbox.db_engine = create_engine(url)

	class Mailbox(Service.Mailbox):
		def __init__(self, owner, **kwargs):
			super(SqlWriter.Mailbox, self).__init__(owner, **kwargs)
			self.db_engine = None
			self.db_session = None