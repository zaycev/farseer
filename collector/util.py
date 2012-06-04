# -*- coding: utf-8 -*-

import urllib2



class TextFetcher(object):

	def __init__(self, encoding="utf-8", timeout=25):
		self._timeout = timeout
		self._encoding = encoding

	def fetch_text(self, url):
		req = urllib2.urlopen(url)
		encoding = self._encoding
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