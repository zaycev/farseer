# -*- coding: utf-8 -*-
from google.protobuf.descriptor import FieldDescriptor

from sqlalchemy import Integer, Text, Float, Boolean, Binary, MetaData
from sqlalchemy import Table, create_engine
from sqlalchemy.orm import mapper, create_session
from sqlalchemy.engine.url import URL

from collector.core.service import Worker
from collector.core.service import Service
from collector.core.service import Behavior
from options import DATABASE_CONFIG

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


class SqlWorker(Worker):
	name = "worker.sql_worker"

	def init_mailbox(self, mailbox, **kwargs):
		url = URL(
			DATABASE_CONFIG["arxiv"]["driver"],
			username=DATABASE_CONFIG["arxiv"]["user"],
			password=DATABASE_CONFIG["arxiv"]["password"],
			host=DATABASE_CONFIG["arxiv"]["host"],
			port=DATABASE_CONFIG["arxiv"]["port"],
			database=DATABASE_CONFIG["arxiv"]["database"],
		)
		mailbox.db_engine = create_engine(url)
		mailbox.db_metadata = MetaData(bind=mailbox.db_engine)

	@staticmethod
	def sql_table_name(task):
		if task.sql_table_name:
			return task.sql_table_name.replace(".", "_")
		return task.name.replace(".", "_")

	class Mailbox(Service.Mailbox):
		def __init__(self, owner, **kwargs):
			super(SqlWriter.Mailbox, self).__init__(owner, **kwargs)
			self.db_engine = None
			self.db_session = None
			self.db_metadata = None
			self.db_tabs = {}

class SqlReader(SqlWorker):
	name = "worker.sql_worker"
	behavior_mode = Behavior.PROC
	window_size = 128
	window_sleep_time = 4

	def target(self, task):
		pass


class SqlWriter(SqlWorker):
	name = "worker.sql_writer"
	behavior_mode = Behavior.PROC

	def target(self, task):
		mailbox = self.mailbox
		if task.name not in mailbox.db_tabs:
			new_tab_name = SqlWriter.sql_table_name(task)
			tab = Table(new_tab_name, mailbox.db_metadata, *task.__columns__())
			tab_type = type("tb-{0}".format(len(mailbox.db_tabs)), (object,), {})
			mapper(tab_type, tab)
			mailbox.db_tabs[task.name] = (tab, tab_type)
			mailbox.db_session = create_session(bind=mailbox.db_engine,
				autocommit=True, autoflush=True)
			try:
				mailbox.db_metadata.create_all(mailbox.db_engine)
			except Exception:
				# TODO: remove this printings
				self.log(traceback.format_exc())
		else:
			tab_type = mailbox.db_tabs[task.name][1]
		tmp = tab_type()
		task.copy_to(tmp)
		mailbox.db_session.begin()
		mailbox.db_session.add(tmp)
		mailbox.db_session.commit()
		return []