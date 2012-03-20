# -*- coding: utf-8 -*-
from abc import ABCMeta
from abc import abstractmethod

import urllib2

class IWorker(object):
	__metaclass__ = ABCMeta

	class State(object):
		WAIT = 0
		BUSY = 1
		STUCK = 2

	@abstractmethod
	def target(self, *args, **kwargs):
		raise NotImplementedError("You should implement this method")


class AbsDataFetcher(IWorker):

	def __init__(self):
		super(AbsDataFetcher, self).__init__()
		self.fetch_timeout = 45

	def fetch_data(self, url):
		req = urllib2.urlopen(url=url, timeout=self.fetch_timeout)
		return req


class TextDataFetcher(AbsDataFetcher):

	def __init__(self, encoding="utf-8"):
		super(TextDataFetcher, self).__init__()
		self.encoding = encoding

	def fetch_text(self, url):
		req = super(TextDataFetcher, self).fetch_data(url)
		encoding = self.encoding
		try:
			content_type_params = req.info().getplist()
			for param in content_type_params:
				try:
					key, value = param.split("=")
				except Exception: continue
				if key == "charset":
					encoding = value
					break
		except Exception: pass
		return unicode(req.read(), encoding)

	def target(self, url):
		return self.fetch_data(url)