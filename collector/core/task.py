# -*- coding: utf-8 -*-
from collector_pb2 import Job, JobMeta, JobExample
from collector.core.orm import PROTOBUFF_SQL_MAP
from google.protobuf.descriptor import FieldDescriptor
from sqlalchemy import Column, Integer

import time as T

class Task(object):
	max_print_str_length = 64
	name = "sys.task.base"
	jobt = Job
	# sql = None
	
	def __init__(self, job_proto=None):
		time = T.time() + T.timezone
		self.job = self.jobt()
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
		print_str = u"\n───{0}".format(self.name)
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
		print_str += u"\n"
		return print_str.encode('utf-8')

	def __str__(self):
		return self.__unicode__()

	def __columns__(self):
		cols=[Column('id', Integer, primary_key=True)]
		for field_descr, _ in self.job.ListFields():
			sql_type = PROTOBUFF_SQL_MAP[field_descr.type]
			if sql_type != None:
				cols.append(Column(field_descr.name, sql_type, primary_key=False))
		return cols

	def copy_to(self, object):
		for field_descr, val in self.job.ListFields():
			setattr(object, field_descr.name, val)

class TaskExample(Task):
	name = "sys.task.example"
	jobt = JobExample