# -*- coding: utf-8 -*-

from supervisor import AbsSupervisor
from collector.workers import RiverFetcherAgent
from collector.workers import LinkSpotterAgent
from collector.workers import PageFetcherAgent

class RiverFetcher(AbsSupervisor):
	name = "River Fetcher"

	def __init__(self, address):
		super(RiverFetcher, self).__init__(address, RiverFetcherAgent)

	def __default_params__(self):
		return (
			("pool_size", 32),
		),(
			("bundle_key", ""),
			("start_page", 2),
			("pages_count", 1000),
			("dataset", ""),
		)

	def __get_state__(self):
		return (),()


class LinkSpotter(AbsSupervisor):
	name = "Link Spotter"

	def __init__(self, address):
		super(LinkSpotter, self).__init__(address, LinkSpotterAgent)

	def __default_params__(self):
		return (
			("pool_size", 2),
		),(
			("bundle_key", ""),
			("input_dataset", ""),
			("output_dataset", ""),
		)

	def __get_state__(self):
		return (),()


class PageFetcher(AbsSupervisor):
	name = "Page Fetcher"

	def __init__(self, address):
		super(PageFetcher, self).__init__(address, PageFetcherAgent)

	def __default_params__(self):
		return (
			("pool_size", 128),
		),(
			("input_dataset", ""),
			("output_dataset", ""),
		)

	def __get_state__(self):
		return (),()