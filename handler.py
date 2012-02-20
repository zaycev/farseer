# -*- coding: utf-8 -*-

class CollectorHandler(object):

	def __init__(self, **kwargs):
		if "size" not in kwargs:
			kwargs["size"] = 1
		self.params = kwargs