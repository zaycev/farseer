# -*- coding: utf-8 -*-
from apps.bi.task import BiFormHubUriTask
from apps.bi.task import BiHubDwTask
from apps.bi.settings import HUB_URI_PATTERN
from collector.core import Worker

class BiHubUriFormer(Worker):
	name = "worker.hub_addr"
	
	@staticmethod
	def __target__(task):
		hub_uris = []
		for page_num in xrange(task["f"], task["t"] + 1):
			hub_uri = HUB_URI_PATTERN.format(page_num)
			hub_uris.append(BiHubDwTask(uri=hub_uri))
		return hub_uris