# -*- coding: utf-8 -*-

import sys
import time
import datetime

from lxml.html import document_fromstring
from lxml.html.clean import clean_html

from collector.core import Worker
from collector.core import Task
from collector.core import WkUrlFetcher
from collector.core.orm import SqlWriter

from apps.bi.protocol_pb2 import DataAuthor
from apps.bi.protocol_pb2 import DataComment

from apps.bi.protocol_pb2 import JobHubRange
from apps.bi.protocol_pb2 import JobHubUri
from apps.bi.protocol_pb2 import JobRawHub
from apps.bi.protocol_pb2 import JobRawTopic

from apps.bi.task import TaskHubRange
from apps.bi.task import TaskHubUri
from apps.bi.task import TaskRawHub
from apps.bi.task import TaskRawTopic

class WkParser(Worker):
	name = "worker.parser"
	
	@staticmethod
	def find_class(el, class_name, default_index=0):
		matched = el.find_class(class_name)
		if len(matched):
			return matched
		else:
			raise Exception("no elements found in {0} by class {1}"\
				.format(el.tag, class_name))



class WkHubUriFormer(Worker):
	name = "worker.hub_uri_former"
	template = u"http://www.businessinsider.com/?page={0}"
	
	def gen_uri(self, page_num):
		if page_num > 0:
			return self.template.format(page_num)
		return None

	def __target__(self, task, **kwargs):
		hub_uri_list = []
		if not(task.job.f and task.job.t) and not task.job.sample:
			raise Exception("{0}: wrong args".format(self.name))
		if task.job.f and task.job.t:
			for page_num in xrange(task.job.f, task.job.t + 1):
				new_uri = self.gen_uri(page_num)
				if new_uri:
					new_job = JobHubUri(uri=new_uri)
					new_task = TaskHubUri(new_job)
					hub_uri_list.append(new_task)

		if task.job.sample:
			for page_num in task.job.sample:
				new_uri = self.gen_uri(page_num)
				if new_uri:
					new_job = JobHubUri(uri=new_uri)
					new_task = TaskHubUri(new_job)
					hub_uri_list.append(new_task)

		return hub_uri_list


class WkHubFetcher(WkUrlFetcher):
	name = "worker.hub_fetcher"
	
	def __target__(self, task, **kwargs):
		html = self.fetch_html(task.job.uri)
		return [TaskRawHub(JobRawHub(html=html))]


class WkHubParser(WkParser):
	name = "worker.hub_parser"

	def extract_image_uri(self, post_et):
		try:
			img = self.find_class(post_et,"river-thumb")[0]
			if img.tag == "img":
				return img.get("src")
		except:
			return None

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
		title_div = None
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
		for el in excerpt:
			if el.tag == "p":
				return el.text
		return None

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
		
	def __target__(self, task, **kwargs):

		html = task.job.html
		hub_doc = document_fromstring(html)
		river = hub_doc.find_class("river")[0]
		tasks = []
		
		for post_et in river:
			
			tag = post_et.tag
			cls = post_et.attrib.get("class", [])
			
			if tag == "div" and ("yui-gd" in cls or "river-post" in cls):
				
				post_uri, title = self.extract_title(post_et)
				time = self.extract_time(post_et)
				image_uri = self.extract_image_uri(post_et)
				short_text = self.extract_short_text(post_et)
				comments = self.extract_comments(post_et)
				views = self.extract_views(post_et)
				authors = self.extract_author(post_et)

				new_job = JobRawTopic(
					uri = post_uri,
					title = title,
					image_uri = image_uri,
					short_text = short_text,
					comments = comments,
					views = views,
					time = time,
				)

				for uri, name in authors:
					new_author = new_job.authors.add()
					new_author.name = name
					new_author.uri = uri
					new_author.type = DataAuthor.TOPIC

				tasks.append(TaskRawTopic(new_job))

		return tasks

		
class WkTopicFetcher(WkUrlFetcher):
	name = "worker.topic_fetcher"
	
	def __target__(self, task, **kwargs):
		html = self.fetch_html(task.job.uri)
		task.job.html = html
		return [task]
		
class WkTopicParser(WkParser):
	name = "worker.topic_parser"
		
	def __target__(self, task, **kwargs):
		html = clean_html(task.job.html)
		hub_doc = document_fromstring(html)
		content_el = hub_doc.find_class("KonaBody post-content")[0]
		full_text = ""
		for el in content_el:
			if el.tag in ["p", "ul", "ol", "strong"]:
				full_text = "".join([full_text, el.text_content()])

		task.job.full_text = full_text
		return [task]

from sqlalchemy import Table
from sqlalchemy.orm import mapper, create_session

class WkTopicSqlWriter(SqlWriter):
	name = "worker.topic_sql_writer"

	class SqlTmp(object):
		pass

	def __target__(self, task, **kwargs):
		pass
		mailbox = kwargs["mailbox"]
		if task.name not in mailbox.db_tabs:
			t = Table(task.name, mailbox.db_metadata, *task.__columns__())
			mapper(WkTopicSqlWriter.SqlTmp, t)
			mailbox.db_tabs[task.name] = t
			mailbox.db_session = create_session(bind=mailbox.db_engine,
				autocommit=False, autoflush=True)
		tmp = WkTopicSqlWriter.SqlTmp()
		task.copy_to(tmp)
		mailbox.db_session.add(tmp)
		mailbox.db_session.commit()
		return []