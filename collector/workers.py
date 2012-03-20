# -*- coding: utf-8 -*-

from collector.models import RawRiver
from worker import TextDataFetcher
from agent import AbsAgentWorker

class RiverFetcher(TextDataFetcher):

	def __init__(self, source):
		super(RiverFetcher, self).__init__()
		self.source = source

	def fetch_river(self, page):
		url = self.source.make_river_url(page)
		body = self.fetch_text(url)
		raw_river = RawRiver(url=url, body=body, mime_type="text/html",
							source=self.source)
		return raw_river

class RiverFetherAgent(AbsAgentWorker):
	worker_class = RiverFetcher

	def init_worker(self, params):
		pass