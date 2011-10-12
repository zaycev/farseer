# -*- coding: utf-8 -*-
import json
import unittest

from protobuff_pb2 import Task as PbTask
from protobuff_pb2 import ExampleTask as PbExampleTask

from datetime import datetime as DT

class Task(object):
	name = "sys.task.base"
	pb = PbTask

	def __init__(self, **kwargs):
		self.data = self.pb()
		self.data.meta.time = str(DT.now())
		self.data.meta.name = self.name

	def __getstate__(self):
		return self.data.SerializeToString()
	
	def __setstate__(self, state):
		self.data = self.pb()
		self.data.ParseFromString(state)
		
	def __unicode__(self):
		return u"{0}".format(self.name)
	
	def __str__(self):
		return self.__unicode__()

class ExampleTask(Task):
	name = "sys.task.example"
	pb = PbExampleTask

	def __init__(self, text=None):
		super(ExampleTask, self).__init__()
		if text:
			self.data.text = text
