# -*- coding: utf-8 -*-

from supervisor import AbsSupervisor
from collector.workers import RiverFetcherAgent
from collector.workers import LinkXSpotterAgent

class RiverFetchingSupervisor(AbsSupervisor):
	name = "River Fetcher"

	def __init__(self, address):
		super(RiverFetchingSupervisor, self).__init__(address,
			RiverFetcherAgent)

	def __default_params__(self):
		return (
			("pool_size", 48),
		),(
			("source_id", 1),
			("start_page", 5),
			("pages_count", 1000),
			("dataset", "new dataset"),
		)

	def __get_state__(self):
		return (),()


class LinkXSpotter(AbsSupervisor):
	name = "Link XSpotter"

	def __init__(self, address):
		super(LinkXSpotter, self).__init__(address,
			LinkXSpotterAgent)

	def __default_params__(self):
		return (
			("pool_size", 2),
		),(
			("input_source_id", 1),
			("input_dataset", ""),
			("output_dataset", ""),
			("link_xpath", "/html/body/div[2]/div[3]/div[1]/div[1]/div/div/div/article/div[2]/header/div[2]/a/@href")
		)

	def __get_state__(self):
		return (),()