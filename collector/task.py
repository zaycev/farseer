# -*- coding: utf-8 -*-
from collector_pb2 import Job, JobMeta, JobExample, JobOrmReaderRange
from collector.orm import PROTO_BUFF_SQL_MAP
from google.protobuf.descriptor import FieldDescriptor
from sqlalchemy import Column, Integer
import pickle

import time as T

class Task(object):
	max_print_str_length = 192
	max_fails = 512
	name = "sys.task.base"
	jobt = Job

	sql_table_name = None
	sql_exclude_fields = None
	sql_type_map = None
	sql_value_map = None

	def __init__(self, job_proto=None):
		time = T.time() + T.timezone
		self.job = self.jobt()
		if job_proto:
			self.job.CopyFrom(job_proto)
		meta = JobMeta(time=time, name=self.name, fails=0)
		self.job.meta.CopyFrom(meta)

	def __getstate__(self):
		return self.job.SerializeToString()
	
	def __setstate__(self, state):
		self.job = self.jobt()
		self.job.ParseFromString(state)

	def serialize(self):
		return pickle.dumps(self)

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

	@staticmethod
	def __extract_fields__(job):
		"""
		Extracts not null fields as a list of tuples where each tuple
		is (<name>, <type>, <value>). If job class has nested
		messages, their internal field names will be transformed
		using the following formula: <message name> + _ + <field name>.
		"""
		fields = []
		for field_descr, field_val in job.ListFields():
			if field_descr.type == FieldDescriptor.TYPE_MESSAGE:
				new_fields = Task.__extract_fields__(field_val)
				for field_name, field_type, field_val in new_fields:
					fields.append((field_descr.name + "_" + field_name, field_type, field_val))
			else:
				fields.append((field_descr.name, field_descr.type, field_val))
		return fields


	def __columns__(self):
		"""
		Returns a list of colums representing self job
		message class. Colums have type of SqlAlchemy Column
		"""
		cols=[Column('id', Integer, primary_key=True, autoincrement=True)]
		fields = Task.__extract_fields__(self.job)
		for field_name, field_type, _ in fields:
			if self.sql_exclude_fields is not None and\
			   field_name in self.sql_exclude_fields:
				pass
			else:
				if self.sql_type_map is not None and\
					field_name in self.sql_type_map:
					sql_type = self.sql_type_map[field_name]
				else:
					sql_type = PROTO_BUFF_SQL_MAP[field_type]
				if sql_type is not None:
					cols.append(Column(field_name, sql_type, primary_key=False))
		return cols

	def copy_to(self, object):
		fields = Task.__extract_fields__(self.job)
		for field_name, field_type, field_val in fields:
			if self.sql_exclude_fields is not None and\
			   field_name in self.sql_exclude_fields:
				pass
			else:
				if self.sql_value_map and\
				   field_name in self.sql_value_map:
					value = self.sql_value_map[field_name](field_val)
				else:
					value = field_val
				setattr(object, field_name, value)

def deserialize(task_blob):
	return pickle.loads(task_blob)