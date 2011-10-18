# -*- coding: utf-8 -*-
from apps.bi.task import BiHubDwTask
from apps.bi.task import BiHubParseTask
from collector.core import Worker
from collector.core import Task
import urllib

HUB_URI_PATTERN = u"http://www.businessinsider.com/?page={0}"

class SimpleFileWriter(Worker):
	name = "worker.f_writer"
	file_pattern = u"/tmp/bi/{0}.gpt"
	@staticmethod
	def __target__(task):
		f = open(SimpleFileWriter.file_pattern.format(task.data.meta.time), mode="w")
		f.write(task.__getstate__())
		f.close()
		return []


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
		uri = task.data.uri
		req = urllib.urlopen(url=uri)
		try:
			enc = req['content-type'].split('charset=')[-1]
		except:
			enc = "utf-8"
		data = req.read()
		html = unicode(data, enc)
		return [BiHubParseTask(html=html)]