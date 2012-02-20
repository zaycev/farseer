# -*- coding: utf-8 -*-
# This module contains some generic worker types such as an html fetcher

import urllib2
from collector.service import Worker
from collector.service import Behavior

class WkTextDataFetcher(Worker):
	behavior_mode = Behavior.THREAD
	name = "worker.fetcher"
	fetch_timeout = 45
	def_enc = "utf-8"
	
	def fetch_text(self, uri):
		req = urllib2.urlopen(url=uri, timeout=self.fetch_timeout)
		try:
			content_type = req["content-type"]
			chunks = content_type.split("charset=")
			enc = chunks[-1] if len(chunks) > 0 else self.def_enc
		except:
			enc = self.def_enc
		data = req.read()
		text_data = unicode(data, enc)
		return text_data

class WkParser(Worker):
	immortal = True
	behavior_mode = Behavior.PROC
	name = "worker.parser"
	text_content_allowed_containers = {"p", "ul", "ol", "dl", "strong", "span", "a"}

	@staticmethod
	def text_content(content_el, exclude={}):
		full_text = ""
		containers = WkParser.text_content_allowed_containers
		for el in content_el:
			if el.tag in containers and el.tag not in exclude:
				full_text = "".join([full_text, "\n", el.text_content()])
		return full_text

	@staticmethod
	def find_class(el, class_name):
		matched = el.find_class(class_name)
		if len(matched):
			return matched
		else:
			raise Exception("no elements found in {0} by class {1}"\
			.format(el.tag, class_name))