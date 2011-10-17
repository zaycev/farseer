# -*- coding: utf-8 -*-
from collector.core.task import Task
from apps.bi.bi_pb2 import BiFormHubUriTask as PbBiFormHubUriTask
from apps.bi.bi_pb2 import BiHubDwTask as PbBiHubDwTask
from apps.bi.bi_pb2 import BiTopicDwTask as PbBiTopicDwTask
from apps.bi.bi_pb2 import BiHubParseTask as PbBiHubParseTask


class BiFormHubUriTask(Task):
	name = "task.hub_addr"
	pb = PbBiFormHubUriTask
	
	def __init__(self, **kwargs):
		super(BiFormHubUriTask, self).__init__()
		self.data.f = kwargs.get("f")
		self.data.t = kwargs.get("t")


class BiHubDwTask(Task):
	name = "task.hub_dw"
	pb = PbBiHubDwTask
	
	def __init__(self, **kwargs):
		super(BiHubDwTask, self).__init__()
		self.data.uri = kwargs.get("uri")


class BiHubParseTask(Task):
	name = "task.hub_parse"
	pb = PbBiHubParseTask

	def __init__(self, **kwargs):
		super(BiHubParseTask, self).__init__()
		self.data.html = kwargs.get("html")


class BiTopicDwTask(Task):
	name = "task.topic_dw"
	pb = PbBiTopicDwTask

	def __init__(self, **kwargs):
		super(BiTopicDwTask, self).__init__()
		self.data.uri = kwargs.get("uri")
		self.data.title = kwargs.get("title")
		self.data.time = kwargs.get("time")
		self.data.short_text = kwargs.get("short_text")
		self.data.views = kwargs.get("views")
		self.data.comments = kwargs.get("comments")
		self.data.image = kwargs.get("image")
		self.data.author = kwargs.get("author")
		self.data.response = kwargs.get("response")