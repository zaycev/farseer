# -*- coding: utf-8 -*-
from apps.bi.task import BiFormHubAddress
from collector.core import Worker

class BiHubFormer(Worker):
	name = "worker.hub_dw"
	
	@staticmethod
	def __target__(task):
		pass