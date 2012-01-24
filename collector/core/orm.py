# -*- coding: utf-8 -*-
from google.protobuf.descriptor import FieldDescriptor

from sqlalchemy import Integer, Text, Float, Boolean, Binary, MetaData
from sqlalchemy import Table, create_engine
from sqlalchemy.orm import mapper, create_session
from sqlalchemy.engine.url import URL

from collector.core.service import Worker
from collector.core.service import Service
from collector.core.service import Behavior
from settings import ORM_CONFIG

import traceback

PROTO_BUFF_SQL_MAP = {
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

class SqlWriter(Worker):
	name = "worker.sql_writer"
	behavior_mode = Behavior.PROC

	def init_mailbox(self, mailbox, **kwargs):
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

	def target(self, task):
		mailbox = self.mailbox
		if task.name not in mailbox.db_tabs:
			new_tab_name = SqlWriter.sql_table_name(task)
			tab = Table(new_tab_name, mailbox.db_metadata, *task.__columns__())
			tab_type = type("tb-{0}".format(len(mailbox.db_tabs)), (object,), {})
			mapper(tab_type, tab)
			mailbox.db_tabs[task.name] = (tab, tab_type)
			mailbox.db_session = create_session(bind=mailbox.db_engine,
				autocommit=False, autoflush=True)
			try:
				mailbox.db_metadata.create_all(mailbox.db_engine)
			except Exception:
				# TODO: remove this printings
				self.log(traceback.format_exc())
		else:
			tab_type = mailbox.db_tabs[task.name][1]
		tmp = tab_type()
		task.copy_to(tmp)
		mailbox.db_session.add(tmp)
		mailbox.db_session.commit()
		return []

	@staticmethod
	def sql_table_name(task):
		return task.name.replace(".", "_")

	class Mailbox(Service.Mailbox):
		def __init__(self, owner, **kwargs):
			super(SqlWriter.Mailbox, self).__init__(owner, **kwargs)
			self.db_engine = None
			self.db_session = None
			self.db_metadata = None
			self.db_tabs = {}

	class SqlMapper(object):
		field_value_mapper = {}
		field_type_mapper = {}