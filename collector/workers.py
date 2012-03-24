# -*- coding: utf-8 -*-

import django.db

from worker import Worker
from worker import WorkerIOHelper
from worker import TextFetching

from collector.models import DocumentSource
from collector.models import DataSet
from collector.models import RawRiver
from collector.models import ExtractedUrl

from lxml.html import fromstring


################################################################################
# River Fethcing ###############################################################
################################################################################

class RiverFetcherAgent(Worker):

	def __init_worker__(self, params):
		source = DocumentSource.objects\
			.get(id=params["specific"]["source_id"])
		self.dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["dataset"])
		self.fetcher = RiverFetcher(source)
		if not created:
			self.dataset.sources.add(source)
			self.dataset.save()

	def do_work(self, page_id):
		raw_river = self.fetcher.fetch_river(page_id)
		raw_river.dataset = self.dataset
		return self.serializer.serialize([raw_river])

	@staticmethod
	def make_io_helper(params):
		return RawRiverIOHelper(params)


class RawRiverIOHelper(WorkerIOHelper):

	def __init__(self, params):
		django.db.close_connection()
		super(RawRiverIOHelper, self).__init__(params)
		self.pages_count = int(params["specific"]["pages_count"])
		self.start_page = int(params["specific"]["start_page"])
		self.source_id = int(params["specific"]["source_id"])
		self.doc_source = DocumentSource.objects.get(id=self.source_id)
		self.task_iter = xrange(self.start_page,
								self.start_page + self.pages_count).__iter__()

	@property
	def total_tasks(self):
		return self.pages_count


class RiverFetcher(TextFetching):

	def __init__(self, source):
		super(RiverFetcher, self).__init__()
		self.source = source

	def fetch_river(self, page_offset):
		url = self.source.make_river_url(page_offset)
		body = self.fetch_text(url)
		raw_river = RawRiver(url=url, body=body, mime_type="text/html",
			source=self.source)
		return raw_river


################################################################################
# River Fethcing ###############################################################
################################################################################

class LinkXSpotterAgent(Worker):

	def __init_worker__(self, params):
		self.link_xpath = params["specific"]["link_xpath"]
		self.input_source = DocumentSource.objects\
			.get(id=params["specific"]["input_source_id"])
		self.input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		self.output_dataset, created = DataSet.objects.\
			get_or_create(name=params["specific"]["output_dataset"])
		if not created:
			self.output_dataset.sources.add(self.input_source)
			self.output_dataset.save()

	def do_work(self, raw_river):
		tree = fromstring(raw_river.body)
		urls = tree.xpath(self.link_xpath)
		worker_output = []
		for url in urls:
			extracted_url = ExtractedUrl(
				url = url,
				river = raw_river,
				dataset = self.output_dataset,
			)
			worker_output.append(extracted_url)
		return self.serializer.serialize(worker_output)

	@staticmethod
	def make_io_helper(params):
		return RiverLinkIOHelper(params)


class RiverLinkIOHelper(WorkerIOHelper):

	def __init__(self, params):
		django.db.close_connection()
		super(RiverLinkIOHelper, self).__init__(params)
		self.input_source = DocumentSource.objects\
			.get(id=params["specific"]["input_source_id"])
		self.input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		self.rivers = RawRiver.objects\
			.filter(dataset=self.input_dataset, source=self.input_source)
		self.rivers_count = self.rivers.count()
		self.task_iter = self.rivers.__iter__()

	@property
	def total_tasks(self):
		return self.rivers_count