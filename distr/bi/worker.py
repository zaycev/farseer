# -*- coding: utf-8 -*-

import time
import datetime

from lxml.html import document_fromstring
from lxml.html.clean import clean_html

from collector.core import Worker
from collector.core import WkTextDataFetcher
from collector.core import WkParser
from collector.core import Behavior
from collector.core import SqlReader

from distr.bi.protocol_pb2 import JobRiverUri
from distr.bi.protocol_pb2 import JobRawRiver
from distr.bi.protocol_pb2 import JobRawTopic

from distr.bi.task import TaskRiverUri
from distr.bi.task import TaskRawRiver
from distr.bi.task import TaskRawTopic

class WkRiverUriFormer(Worker):
	name = "worker.river_uri_former"
	template = u"http://www.businessinsider.com/?page={0}"

	def gen_uri(self, page_num):
		if page_num > 0:
			return self.template.format(page_num)
		return None

	def target(self, task):
		river_uri_list = []
		if not(task.job.f and task.job.t) and not task.job.sample:
			raise Exception("{0}: wrong args".format(self.name))
		if task.job.f and task.job.t:
			for page_num in xrange(task.job.f, task.job.t + 1):
				new_uri = self.gen_uri(page_num)
				if new_uri:
					new_job = JobRiverUri(uri=new_uri)
					new_task = TaskRiverUri(new_job)
					river_uri_list.append(new_task)

		if task.job.sample:
			for page_num in task.job.sample:
				new_uri = self.gen_uri(page_num)
				if new_uri:
					new_job = JobRiverUri(uri=new_uri)
					new_task = TaskRiverUri(new_job)
					river_uri_list.append(new_task)
		return river_uri_list


class WkRiverFetcher(WkTextDataFetcher):
	name = "worker.river_fetcher"

	def target(self, task):
		html = self.fetch_text(task.job.uri)
		return [TaskRawRiver(JobRawRiver(html=html, uri=task.job.uri))]


class WkRiverParser(WkParser):
	name = "worker.river_parser"
	behavior_mode = Behavior.PROC

	def extract_image_uri(self, post_et):
		try:
			img = self.find_class(post_et,"river-thumb")[0]
			if img.tag == "img":
				return img.get("src")
		except:
			return "None"

	def extract_author(self, post_et):
		byline = self.find_class(post_et,"byline")[0]
		authors = []
		for el in byline:
			if el.tag == "a":
				uri = el.get("href")
				name = el.text
				authors.append((uri, name,))
		return authors

	def extract_title(self, post_et):
		try:
			title_div = self.find_class(post_et,"river-post yui-u")[0]
		except:
			title_div = post_et
		for el in title_div:
			if el.tag == "h2":
				for el2 in el:
					if el2.tag == "a":
						uri = el2.get("href")
						title = el2.text
						return uri, title

	def extract_time(self, post_et):
		s = self.find_class(post_et,"date")[0].text
		t = None
		try:
			t = datetime.datetime.strptime(s,"%b. %d, %Y, %I:%M %p")
		except:
			dt = datetime.datetime.strptime(s,"%b. %d, %I:%M %p")
			year = datetime.datetime.now().year
			t = datetime.datetime(year, dt.month, dt.day, dt.hour, dt.minute)
		return time.mktime(t.timetuple()) if t else 0

	def extract_short_text(self, post_et):
		excerpt = self.find_class(post_et, "excerpt")[0]
		return self.text_content(excerpt, exclude={"a"})

	def extract_comments(self, post_et):
		byline = self.find_class(post_et,"byline")[0]
		for el in byline:
			if el.tag == "nobr" and el.get("title") == "Read comments":
				for el2 in el:
					if el2.tag == "a" and el2.get("class") == "comment_count":
						if el2.text:
							return int(el2.text)
						return 0
		return 0

	def extract_views(self, post_et):
		byline = self.find_class(post_et,"byline")[0]
		for el in byline:
			if el.tag == "nobr":
				for el2 in el:
					if el2.tag == "span" and el2.get("title") == "views":
						if el2.text:
							text = el2.text.replace(",","")
							return int(text)
						return 0
		return 0

	def target(self, task):
		html = task.job.html
		river_doc = document_fromstring(html)
		river = river_doc.find_class("river")[0]
		tasks = []

		for post_et in river:
			tag = post_et.tag
			cls = post_et.attrib.get("class", [])

			if tag == "div" and ("yui-gd" in cls or "river-post" in cls):

				uri, title = self.extract_title(post_et)

				if "http://www.businessinsider" in uri:

					try:

						tm = self.extract_time(post_et)
						views = self.extract_views(post_et)
						comments = self.extract_comments(post_et)
						short_text = self.extract_short_text(post_et)
						image_uri = self.extract_image_uri(post_et)

						# authors = self.extract_author(post_et)
						new_job = JobRawTopic()
						new_job.post_river_uri = task.job.uri
						new_job.post_uri = uri
						new_job.post_title = title
						new_job.post_time = tm
						new_job.post_views_qti = views
						new_job.post_comments_qti = comments
						new_job.post_short_text = short_text
						if image_uri is not None:
							new_job.post_image_uri = image_uri

						tasks.append(TaskRawTopic(new_job))

					#				for uri, name in authors:
					#					new_author = new_job.authors.add()
					#					new_author.name = name
					#					new_author.uri = uri
					#					new_author.type = DataAuthor.TOPIC
					except:
						pass

		return tasks

class WkTopicFetcher(WkTextDataFetcher):
	name = "worker.topic_fetcher"

	def target(self, task):
		html = self.fetch_text(task.job.post_uri)
		task.job.html = html
		return [task]

class WkTopicParser(WkParser):
	name = "worker.topic_parser"
	behavior_mode = Behavior.PROC

	def target(self, task):
		html = clean_html(task.job.html)
		river_doc = document_fromstring(html)
		content_el = river_doc.find_class("KonaBody post-content")[0]
		task.job.html = html
		task.job.full_text = self.text_content(content_el)
		return [task]

class WkRawTopicReader(SqlReader):
	name = "worker.topic_reader"
	sql_input_task = TaskRawTopic