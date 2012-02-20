# -*- coding: utf-8 -*-
import datetime

from collector.task import Task

from distr.bi.protocol_pb2 import JobRiverRange
from distr.bi.protocol_pb2 import JobRiverUri
from distr.bi.protocol_pb2 import JobRawRiver
from distr.bi.protocol_pb2 import JobRawTopic

from sqlalchemy import DateTime

class TaskRiverRange(Task):
	name = "task.river_range"
	jobt = JobRiverRange
	
	def __init__(self, *args, **kwargs):
		super(TaskRiverRange, self).__init__()
		if "f" in kwargs and "t" in kwargs:
			self.job.f = kwargs["f"]
			self.job.t = kwargs["t"]
		if "sample" in kwargs:
			for number in kwargs["sample"]:
				self.job.sample.append(number)

class TaskRiverUri(Task):
	name = "task.river_uri"
	jobt = JobRiverUri


class TaskRawRiver(Task):
	name = "task.river_raw"
	jobt = JobRawRiver

class TaskRawTopic(Task):
	name = "task.topic_raw"
	jobt = JobRawTopic
	sql_table_name = "news"
	sql_exclude_fields = {"html"}
	sql_type_map = {"post_time": DateTime}
	sql_value_map = {
		"post_time": lambda float_time: datetime.datetime.fromtimestamp(float_time)
	}