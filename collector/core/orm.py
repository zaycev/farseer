# -*- coding: utf-8 -*-
from google.protobuf.descriptor import FieldDescriptor

from sqlalchemy import Integer, Text, Float, Boolean, Binary, MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import create_session
from sqlalchemy.engine.url import URL

from collector.core.server.service import Worker
from collector.core.server.service import Service
from settings2 import ORM_CONFIG

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

class TaskWriter(Worker):
	name = "worker.task_writer"

class SqlWriter(Worker):
	name = "worker.sql_writer"

	def __before_start__(self, mailbox, **kwargs):
		url = URL(
			ORM_CONFIG["DB_DRIVER"],
			username=ORM_CONFIG["DB_USER"],
			password=ORM_CONFIG["DB_PASSWORD"],
			host=ORM_CONFIG["DB_HOST"],
			port=ORM_CONFIG["DB_PORT"],
			database=ORM_CONFIG["DB_DATABASE"]
		)
		mailbox.db_engine = create_engine(url)
		mailbox.db_metadata = MetaData(bind=mailbox.db_engine)
		self.__init_mapper__(mailbox)

	def __init_mapper__(self, mailbox):
		pass

	class Mailbox(Service.Mailbox):
		def __init__(self, owner, **kwargs):
			super(SqlWriter.Mailbox, self).__init__(owner, **kwargs)
			self.db_engine = None
			self.db_session = None
			self.db_metadata = None
			self.db_tabs = {}