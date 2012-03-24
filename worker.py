# -*- coding: utf-8 -*-
import traceback
import threading
import multiprocessing
from django.core import serializers
from collections import deque
from agent import AbsAgent, Message
from abc import ABCMeta
from abc import abstractmethod

import urllib2

class WorkerIOHelper(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, params):
		self.tasks_read = 0
		self.serializer = serializers.get_serializer("json")()
		self.task_iter = None
		self.deferred_tasks = deque()

	@property
	@abstractmethod
	def total_task(self):
		raise NotImplementedError("You should implement this method")

	def save_output(self, worker_output_json):
		worker_output = self.deserialize(worker_output_json)
		for record in worker_output:
			record.save()

	def deserialize(self, json):
		return serializers.deserialize("json", json)

	def read_next_task(self):
		if len(self.deferred_tasks):
			next_task = self.deferred_tasks.pop()
		else:
			next_task = self.task_iter.next()
		self.tasks_read += 1
		return next_task

	def try_it_later(self, task):
		self.tasks_read -= 1
		self.deferred_tasks.appendleft(task)


class Worker(AbsAgent):
	process = False

	class Status(object):
		WAIT = 0
		BUSY = 1

	def __init__(self, address, params):
		self.params = params
		self.worker = None
		self.serializer = None
		super(Worker, self).__init__(address)

	def __init_agent__(self):
		super(Worker, self).__init_agent__()
		self.serializer = serializers.get_serializer("json")()
		self.__init_worker__(self.params)
		self.params = None

	def __init_worker__(self, params):
		pass

	def __handle_message__(self, message, *args, **kwargs):
		if message.extra is Message.TASK:
			task = message.body
			try:
				result = self.do_work(task)
				self.mailbox.send(result, message.sent_from, Message.DONE)
			except Exception:
				error_str = "%s.__handle_message__: \n%s"\
							% (self.__class__.__name__, traceback.format_exc())
				self.mailbox.send(error_str, message.sent_from, Message.FAIL)
		else:
			error_str = "%s.__handle_message__" \
						"got wrongmessage type: %s %s"\
						% (self.__class__.__name__,
						   message.extra,
						   message.extra_name(message.extra))
			self.mailbox.send(error_str, message.sent_from, Message.FAIL)

	def do_work(self, task):
		pass

	def __is_free__(self):
		return True

	@staticmethod
	def make_io_helper(params):
		raise WorkerIOHelper(params)


class IWork(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def do(self, *args, **kwargs):
		raise NotImplementedError("You should implement this method")


class AbsDataFetching(IWork):

	def __init__(self):
		super(AbsDataFetching, self).__init__()
		self.fetch_timeout = 45

	def fetch_data(self, url):
		req = urllib2.urlopen(url=url, timeout=self.fetch_timeout)
		return req


class TextFetching(AbsDataFetching):

	def __init__(self, encoding="utf-8"):
		super(TextFetching, self).__init__()
		self.encoding = encoding

	def fetch_text(self, url):
		req = super(TextFetching, self).fetch_data(url)
		encoding = self.encoding
		try:
			content_type_params = req.info().getplist()
			for param in content_type_params:
				try:
					key, value = param.split("=")
				except Exception: continue
				if key == "charset":
					encoding = value
					break
		except Exception: pass
		return unicode(req.read(), encoding)

	def do(self, url):
		return self.fetch_data(url)