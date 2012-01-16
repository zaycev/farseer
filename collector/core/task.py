# -*- coding: utf-8 -*-
from collector_pb2 import Job
from collector_pb2 import JobMeta
from collector_pb2 import JobExample

import time as T

class Task(object):
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
		return u"{0}".format(self.name)
	
	def __str__(self):
		return self.__unicode__()
	
class TaskExample(Task):
	name = "sys.task.example"
	jobt = JobExample