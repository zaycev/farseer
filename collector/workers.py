# -*- coding: utf-8 -*-

import bundle

from worker import Worker
from worker import WorkerIOHelper
from worker import TextFetcher

from collector.models import DataSet
from collector.models import RawRiver
from collector.models import ExtractedUrl
from collector.models import RawDocument

################################################################################
# River Fethcing ###############################################################
################################################################################

class RawRiverIOHelper(WorkerIOHelper):

	def __init__(self, params):
		start_page = int(params["specific"]["start_page"])
		pages_count = int(params["specific"]["pages_count"])
		super(RawRiverIOHelper, self).__init__(params)
		self.bundle = bundle.get(params["specific"]["bundle_key"])
		self.pages_count = self.bundle.rivers_count(start_page, pages_count)
		self.task_iter =\
			self.bundle.make_river_link_iterator(start_page, pages_count)

	@property
	def total_tasks(self):
		return self.pages_count

class RiverFetcherAgent(Worker):

	def __init_worker__(self, params):
		self.bundle = bundle.get(params["specific"]["bundle_key"])
		self.doc_source = self.bundle.get_or_create_source()
		self.dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["dataset"])
		if not created: self.dataset.save()
		self.fetcher = TextFetcher()

	def do_work(self, page_url):
		river_body = self.fetcher.fetch_text(page_url)
		raw_river = RawRiver(
			url = page_url,
			body = river_body,
			source = self.doc_source,
			dataset = self.dataset,
			mime_type = self.doc_source.mime_type
		)
		return self.serializer.serialize([raw_river])

	@staticmethod
	def make_io_helper(params):
		return RawRiverIOHelper(params)


################################################################################
# Link Spotting ################################################################
##################w##############################################################

class LinkSpotterAgent(Worker):
	process = True

	def __init_worker__(self, params):
		self.bundle = bundle.get(params["specific"]["bundle_key"])
		self.input_source = self.bundle.get_or_create_source()
		self.output_dataset, created = DataSet.objects.\
			get_or_create(name=params["specific"]["output_dataset"])
		if not created: self.output_dataset.save()

	def do_work(self, raw_river):
		links = self.bundle.spot_links(raw_river.body)
		worker_output = []
		for url in links:
			extracted_url = ExtractedUrl(
				url = url,
				source = self.input_source,
				dataset = self.output_dataset,
			)
			worker_output.append(extracted_url)
		return self.serializer.serialize(worker_output)

	@staticmethod
	def make_io_helper(params):
		return RiverLinkIOHelper(params)


class RiverLinkIOHelper(WorkerIOHelper):

	def __init__(self, params):
		super(RiverLinkIOHelper, self).__init__(params)
		self.bundle = bundle.get(params["specific"]["bundle_key"])
		self.input_source = self.bundle.get_or_create_source()
		self.input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		self.rivers = RawRiver.objects\
			.filter(dataset=self.input_dataset, source=self.input_source)
		self.rivers_count = self.rivers.count()
		print "the count is .... %s " % str(self.rivers_count)
		self.task_iter = self.rivers.__iter__()

	@property
	def total_tasks(self):
		return self.rivers_count


################################################################################
# Link Spotting ################################################################
################################################################################

class PageFetcherAgent(Worker):

	def __init_worker__(self, params):
		self.output_dataset, created = DataSet.objects.\
			get_or_create(name=params["specific"]["output_dataset"])
		if not created: self.output_dataset.save()
		self.fetcher = TextFetcher()

	def do_work(self, url):
		body = self.fetcher.fetch_text(url)
		raw_doc = RawDocument(
			url = url,
			dataset = self.output_dataset,
			body = body,
		)
		return self.serializer.serialize([raw_doc])

	@staticmethod
	def make_io_helper(params):
		return RawDocumentIOHelper(params)


class RawDocumentIOHelper(WorkerIOHelper):

	def __init__(self, params):
		super(RawDocumentIOHelper, self).__init__(params)
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		e_urls = self.input_dataset.unfetched_rawdocs
		self.e_urls_count = e_urls.count()
		self.task_iter = e_urls.values("url").all().__iter__()

	@property
	def total_tasks(self):
		return self.e_urls_count