# -*- coding: utf-8 -*-
from apps.bi.task import BiHubDwTask
from collector.core import Worker

HUB_URI_PATTERN = u"http://www.businessinsider.com/?page={0}"

class BiHubUriFormer(Worker):
	name = "worker.hub_uri_former"
	@staticmethod
	def __target__(task):
		hub_uris_list = []
		for page_num in xrange(task.data.f, task.data.t + 1):
			hub_uri = HUB_URI_PATTERN.format(page_num)
			hub_uris_list.append(BiHubDwTask(uri=hub_uri))
		return hub_uris_list

class BiHubDownloader(Worker):
	name = "worker.hub_downloader"
	@staticmethod
	def __target__(task):
		print "start"
		print task.data.uri
		print "end"
		return [task]