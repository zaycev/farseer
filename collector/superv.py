# -*- coding: utf-8 -*-

from supervisor import AbsSupervisor
from collector.workers import RiverFetcherWkr
from collector.workers import UrlSpotterWkr
from collector.workers import DocumentFetcherWkr
from collector.workers import DocumentParserWkr
from collector.workers import ProbeFetcher


class RiverFetcher(AbsSupervisor):
	name = "River Fetcher"

	def __init__(self, address):
		super(RiverFetcher, self).__init__(address, RiverFetcher)

	def __default_params__(self):
		return (
			("pool_size", 32),
		),(
			("bundle_key", ""),
			("start_page", 2),
			("pages_count", 1000),
			("dataset", ""),
		)


class LinkSpotter(AbsSupervisor):
	name = "Link Spotter"

	def __init__(self, address):
		super(LinkSpotter, self).__init__(address, UrlSpotterWkr)

	def __default_params__(self):
		return (
			("pool_size", 2),
		),(
			("bundle_key", ""),
			("input_dataset", ""),
			("output_dataset", ""),
		)


class PageFetcher(AbsSupervisor):
	name = "Page Fetcher"

	def __init__(self, address):
		super(PageFetcher, self).__init__(address, DocumentFetcherWkr)

	def __default_params__(self):
		return (
			("pool_size", 1),
		),(
			("input_dataset", "RU.look.at.me"),
			("output_dataset", "RU.look.at.me.2"),
		)


class PageParser(AbsSupervisor):
	name = "Page Parser"

	def __init__(self, address):
		super(PageParser, self).__init__(address, DocumentParserWkr)

	def __default_params__(self):
		return (
			("pool_size", 1),
		),(
			("bundle_key", "FORBES"),
			("input_dataset", "EN.Forbes.invest"),
			("output_dataset", "EN.Forbes.invest"),
		)


class SocialStat(AbsSupervisor):
	name = "SM Probe Fetcher"

	def __init__(self, address):
		super(SocialStat, self).__init__(address, ProbeFetcher)

	def __default_params__(self):
		return (
			("pool_size", 8),
		),(
			("bundle_key", "FORBES"),
			("input_dataset", "EN.Forbes.invest"),
			("output_dataset", "EN.Forbes.invest"),
		)