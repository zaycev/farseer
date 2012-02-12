# -*- coding: utf-8 -*-
from collector_pb2 import Job, JobMeta, JobExample, JobOrmReaderRange
from collector.core.orm import PROTO_BUFF_SQL_MAP
from google.protobuf.descriptor import FieldDescriptor
from sqlalchemy import Column, Integer
import pickle

import time as T

class Task(object):
	max_print_str_length = 256
	name = "sys.task.base"
	jobt = Job

	sql_table_name = None
	sql_exclude_fields = None
	sql_type_map = None
	sql_value_map = None

	def __init__(self, job_proto=None):
		time = T.time() + T.timezone
		self.job = self.jobt()
		self.fails_counter = 0
		if job_proto:
			self.job.CopyFrom(job_proto)
		meta = JobMeta(time=time, name=self.name)
		self.job.meta.CopyFrom(meta)

	def __getstate__(self):
		return self.job.SerializeToString()
	
	def __setstate__(self, state):
		self.job = self.jobt()
		self.job.ParseFromString(state)

	def is_correct(self):
		return True
		
	def __unicode__(self):
		print_str = u"───{0}".format(self.name)
		for field_descr, field_val in self.job.ListFields():
			if field_descr.type == FieldDescriptor.TYPE_STRING:
				value_str = field_val\
				if len(field_val) < Task.max_print_str_length\
				else field_val[0:Task.max_print_str_length - 1] + u" ..."
				value_str = u"\"" + value_str + u"\""
			elif field_descr.type == FieldDescriptor.TYPE_MESSAGE:
				value_str = u"<message>"
			else:
				value_str = str(field_val)
			print_str += u"\n   ├───{0} = {1}".format(field_descr.name, value_str)
		return print_str.encode('utf-8')

	def __str__(self):
		return self.__unicode__()

	def __columns__(self):
		cols=[Column('id', Integer, primary_key=True, autoincrement=True)]
		for field_descr, _ in self.job.ListFields():
			if self.sql_exclude_fields is not None and\
			   field_descr.name in self.sql_exclude_fields:
				pass
			else:
				if self.sql_type_map is not None and\
					field_descr.name in self.sql_type_map:
					sql_type = self.sql_type_map[field_descr.name]
				else:
					sql_type = PROTO_BUFF_SQL_MAP[field_descr.type]
				if sql_type is not None:
					cols.append(Column(field_descr.name, sql_type, primary_key=False))
		return cols

	def copy_to(self, object):
		for field_descr, val in self.job.ListFields():
			if self.sql_exclude_fields is not None and\
			   field_descr.name in self.sql_exclude_fields:
				pass
			else:
				value = val
				if self.sql_value_map and\
				   field_descr.name in self.sql_value_map:
					value = self.sql_value_map[field_descr.name](value)
				setattr(object, field_descr.name, value)

class TaskExample(Task):
	name = "sys.task.example"
	jobt = JobExample

class OrmReaderRange(Task):
	name = "sys.task.orm_reader_range"
	jobt = JobOrmReaderRange