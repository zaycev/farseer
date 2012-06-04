# -*- coding: utf-8 -*-

import bundle
from worker import Worker, TaskIO
from collector.util import TextFetcher
from collector.models import DataSet, RawRiver, Url, RawDocument
from collector.models import Document, Author, Probe



class RawRiverIO(TaskIO):
	@property
	def total_tasks(self):
		return self.pages_count

	def __init__(self, params):
		start_page = int(params["specific"]["start_page"])
		pages_count = int(params["specific"]["pages_count"])
		super(RawRiverIO, self).__init__(params)
		self.bundle = bundle.get(params["specific"]["bundle_key"])
		self.pages_count = self.bundle.rivers_count(start_page, pages_count)
		self._task_iter =\
			self.bundle.make_river_link_iterator(start_page, pages_count)



class RiverFetcherWkr(Worker):

	def __init_worker__(self, params):
		self._bundle = bundle.get(params["specific"]["bundle_key"])
		self._doc_source = self._bundle.get_or_create_source()
		self._dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["dataset"])
		if not created: self._dataset.save()
		self._fetcher = TextFetcher()

	def do_work(self, page_url):
		river_body = self._fetcher.fetch_text(page_url)
		raw_river = RawRiver(
			url = page_url,
			body = river_body,
			source = self._doc_source,
			dataset = self._dataset,
			mime_type = self._doc_source.mime_type
		)
		return self._serializer.serialize([raw_river])

	@staticmethod
	def make_task_io(params):
		return RawRiverIO(params)



class RiverLinkIO(TaskIO):
	@property
	def total_tasks(self):
		return self.rivers_count

	def __init__(self, params):
		super(RiverLinkIO, self).__init__(params)
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
		self._task_iter = self.river_body_lazy_iter(river_id_list)
		if not created: self.output_dataset.save()

	def river_body_lazy_iter(self, id_list):
		for new_id in id_list:
			yield RawRiver.objects.values("body").get(id=new_id)["body"]



class UrlSpotterWkr(Worker):
	process = True

	def __init_worker__(self, params):
		self._bundle = bundle.get(params["specific"]["bundle_key"])
		self._input_source = self._bundle.get_or_create_source()
		self._output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])

	def do_work(self, river_body):
		urls = self._bundle.spot_links(river_body)
		extracted_urls = []
		for url in urls:
			extracted_url = Url(
				url = url,
				source = self._input_source,
				dataset = self._output_dataset,
			)
			extracted_urls.append(extracted_url)
		return self._serializer.serialize(extracted_urls)

	@staticmethod
	def make_task_io(params):
		return RiverLinkIO(params)



class RawDocumentIO(TaskIO):
	@property
	def total_tasks(self):
		return self.e_urls_count

	def __init__(self, params):
		super(RawDocumentIO, self).__init__(params)
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		output_dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["output_dataset"])
		e_urls = output_dataset.unfetched_rawdocs(input_dataset)
		self.e_urls_count = e_urls.count()
		unfetched_ids = map(lambda eurl: eurl["id"], e_urls.values("id"))
		self._task_iter = self.url_lazy_iter(unfetched_ids)

		if not created: output_dataset.save()

	@staticmethod
	def url_lazy_iter(id_list):
		for new_id in id_list:
			url = Url.objects.values("url").get(id=new_id)["url"]
			yield url



class DocumentFetcherWkr(Worker):

	def __init_worker__(self, params):
		self._output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])
		self._fetcher = TextFetcher()

	def do_work(self, url):
		body = self._fetcher.fetch_text(url)
		raw_doc = RawDocument(
			url = url,
			dataset = self._output_dataset,
			body = body,
		)
		return self._serializer.serialize([raw_doc])

	@staticmethod
	def make_task_io(params):
		return RawDocumentIO(params)



class DocumentIO(TaskIO):
	@property
	def total_tasks(self):
		return self.rawdocs_count

	def __init__(self, params):
		super(DocumentIO, self).__init__(params)
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		output_dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["output_dataset"])
		rawdocs = output_dataset.rawdocs(input_dataset)
		self.rawdocs_count = rawdocs.count()
		rawdoc_ids = map(lambda rd: rd["id"], rawdocs.values("id"))
		self._task_iter = self.rawdoc_lazy_iter(rawdoc_ids)
		if not created: output_dataset.save()

	@staticmethod
	def rawdoc_lazy_iter(id_list):
		for new_id in id_list:
			rawdoc = RawDocument.objects.get(id=new_id)
			yield rawdoc



class DocumentParserWkr(Worker):
	process = True

	def __init_worker__(self, params):
		self._output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])
		self._bundle = bundle.get(params["specific"]["bundle_key"])

	def do_work(self, rawdoc):
		parsed = self._bundle.extract_essential(rawdoc)
		new_doc = Document(
			url = rawdoc.url,
			dataset = self._output_dataset,
			title = parsed["title"],
			summary = "",
			content = parsed["content"],
			published = parsed["published"],
		)
		authors = [Author(url = url) for url in parsed["author_url"]]
		return self._serializer.serialize([new_doc] + authors)

	@staticmethod
	def make_task_io(params):
		return DocumentIO(params)



class ProbeIO(TaskIO):
	@property
	def total_tasks(self):
		return self.rawdocs_count

	def __init__(self, params):
		super(ProbeIO, self).__init__(params)
		input_dataset = DataSet.objects\
			.get(name=params["specific"]["input_dataset"])
		output_dataset, created = DataSet.objects\
			.get_or_create(name=params["specific"]["output_dataset"])
		rawdocs = input_dataset.rawdocument_set
		self.rawdocs_count = rawdocs.count()
		rawdoc_ids = map(lambda rd: rd["id"], rawdocs.values("id"))
		self._task_iter = self.rawdoc_lazy_iter(rawdoc_ids)
		if not created: output_dataset.save()

	@staticmethod
	def rawdoc_lazy_iter(id_list):
		for new_id in id_list:
			rawdoc = RawDocument.objects.get(id=new_id)
			yield rawdoc



class ProbeFetcher(Worker):
	process = True

	def __init_worker__(self, params):
		self._output_dataset = DataSet.objects\
			.get(name=params["specific"]["output_dataset"])
		self._bundle = bundle.get(params["specific"]["bundle_key"])

	def do_work(self, rawdoc):
		probes = self._bundle.get_probes(rawdoc)
		new_probes = []
		for tag, signal in probes.items():
			new_probe = Probe(
				target = rawdoc.url,
				dataset = self._output_dataset,
				tag = tag,
				signal = signal,
			)
			new_probes.append(new_probe)
		return self._serializer.serialize(new_probes)

	@staticmethod
	def make_task_io(params):
		return ProbeIO(params)
