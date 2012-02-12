# -*- coding: utf-8 -*-

class Tier(object):

	def __init__(self, **kwargs):
		if "qti" not in kwargs:
			kwargs["qti"] = 1
		self.params = kwargs