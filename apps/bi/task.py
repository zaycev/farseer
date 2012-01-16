# -*- coding: utf-8 -*-
import time
import datetime

from collector.core.task import Task

from apps.bi.protocol_pb2 import DataAuthor
from apps.bi.protocol_pb2 import DataComment

from apps.bi.protocol_pb2 import JobHubRange
from apps.bi.protocol_pb2 import JobHubUri
from apps.bi.protocol_pb2 import JobRawHub
from apps.bi.protocol_pb2 import JobRawTopic

class TaskHubRange(Task):
	name = "task.hub_range"
	jobt = JobHubRange
	
	def __init__(self, *args, **kwargs):
		super(TaskHubRange, self).__init__()
		if "f" in kwargs and "t" in kwargs:
			self.job.f = kwargs["f"]
			self.job.t = kwargs["t"]
		if "sample" in kwargs:
			for number in kwargs["sample"]:
				self.job.sample.append(number)

class TaskHubUri(Task):
	name = "task.hub_uri"
	jobt = JobHubUri


class TaskRawHub(Task):
	name = "task.hub_raw"
	jobt = JobRawHub


class TaskRawTopic(Task):
	name = "task.topic_raw"
	jobt = JobRawTopic