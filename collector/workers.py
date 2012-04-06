# -*- coding: utf-8 -*-

import bundle

from worker import Worker
from worker import WorkerIOHelper
from worker import TextFetcher

from collector.models import DataSet
from collector.models import RawRiver
from collector.models import ExtractedUrl
from collector.models import RawDocument
from collector.models import Document
from collector.models import Author
from collector.models import Probe

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
################################################################################

class RiverLinkIOHelper(WorkerIOHelper):

	def __init__(self, params):
		super(RiverLinkIOHelper, self).__init__(params)
		self.bundle = bundle.get(params["specific"]["bundle_key"])
		self.input_source = self.bundle.get_or_create_source()
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		self.output_dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["output_dataset"])
		rivers = RawRiver.objects\
			.filter(dataset=input_dataset, source=self.input_source)
		self.rivers_count = rivers.count()
		river_id_list =  map(lambda riv: riv["id"], rivers.values("id"))
		self.task_iter = self.lazy_river_body_iter(river_id_list)
		if not created: self.output_dataset.save()

	@property
	def total_tasks(self):
		return self.rivers_count

	def lazy_river_body_iter(self, river_id_list):
		for new_id in river_id_list:
			yield RawRiver.objects.values("body").get(id=new_id)["body"]


class LinkSpotterAgent(Worker):
	process = True

	def __init_worker__(self, params):
		self.bundle = bundle.get(params["specific"]["bundle_key"])
		self.input_source = self.bundle.get_or_create_source()
		self.output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])

	def do_work(self, river_body):
		links = self.bundle.spot_links(river_body)
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


################################################################################
# Page Fetching ################################################################
################################################################################

class RawDocumentIOHelper(WorkerIOHelper):

	def __init__(self, params):
		super(RawDocumentIOHelper, self).__init__(params)
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		output_dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["output_dataset"])
		e_urls = output_dataset.unfetched_rawdocs(input_dataset)
		self.e_urls_count = e_urls.count()
		unfetched_ids = map(lambda eurl: eurl["id"], e_urls.values("id"))
		self.task_iter = self.url_lazy_iter(unfetched_ids)

		if not created: output_dataset.save()

	@staticmethod
	def url_lazy_iter(id_list):
		for new_id in id_list:
			url = ExtractedUrl.objects.values("url").get(id=new_id)["url"]
			yield url

	@property
	def total_tasks(self):
		return self.e_urls_count


class PageFetcherAgent(Worker):

	def __init_worker__(self, params):
		self.output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])
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


################################################################################
# Text Extracting ##############################################################
################################################################################

class DocumentIOHelper(WorkerIOHelper):

	def __init__(self, params):
		super(DocumentIOHelper, self).__init__(params)
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		output_dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["output_dataset"])
		rawdocs = output_dataset.rawdocs(input_dataset)
		self.rawdocs_count = rawdocs.count()
		rawdoc_ids = map(lambda rd: rd["id"], rawdocs.values("id"))
		self.task_iter = self.rawdoc_iter(rawdoc_ids)
		if not created: output_dataset.save()

	@staticmethod
	def rawdoc_iter(id_list):
		for new_id in id_list:
			rawdoc = RawDocument.objects.get(id=new_id)
			yield rawdoc

	@property
	def total_tasks(self):
		return self.rawdocs_count


class PageParserAgent(Worker):
	process = True

	def __init_worker__(self, params):
		self.output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])
		self.bundle = bundle.get(params["specific"]["bundle_key"])

	def do_work(self, rawdoc):
		parsed = self.bundle.extract_essential(rawdoc)
		new_doc = Document(
			url = rawdoc.url,
			dataset = self.output_dataset,
			title = parsed["title"],
			summary = "",
			content = parsed["content"],
			published = parsed["published"],
		)
		authors = [Author(url = url) for url in parsed["author_url"]]
		return self.serializer.serialize([new_doc] + authors)

	@staticmethod
	def make_io_helper(params):
		return DocumentIOHelper(params)


################################################################################
# Social Statistics ############################################################
################################################################################


class ProbeIOHelper(WorkerIOHelper):

	def __init__(self, params):
		super(ProbeIOHelper, self).__init__(params)
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		output_dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["output_dataset"])
		rawdocs = input_dataset.rawdocument_set
		self.rawdocs_count = rawdocs.count()
		rawdoc_ids = map(lambda rd: rd["id"], rawdocs.values("id"))
		self.task_iter = self.rawdoc_iter(rawdoc_ids)
		if not created: output_dataset.save()

	@staticmethod
	def rawdoc_iter(id_list):
		for new_id in id_list:
			rawdoc = RawDocument.objects.get(id=new_id)
			yield rawdoc

	@property
	def total_tasks(self):
		return self.rawdocs_count


class SocialStatAgent(Worker):
	process = True

	def __init_worker__(self, params):
		self.output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])
		self.bundle = bundle.get(params["specific"]["bundle_key"])

	def do_work(self, rawdoc):
		probes = self.bundle.get_probes(rawdoc)
		# print probes
		new_probes = []
		for tag, signal in probes.items():
			new_probe = Probe(
				target = rawdoc.url,
				dataset = self.output_dataset,
				tag = tag,
				signal = signal,
			)
			new_probes.append(new_probe)
		# print "DONE %s" % rawdoc.url
		# print new_probes
		return self.serializer.serialize(new_probes)

	@staticmethod
	def make_io_helper(params):
		return ProbeIOHelper(params)
