# -*- coding: utf-8 -*-

from collections import deque
from django.core import serializers
from django.db import transaction
from agent import AbsAgent
from agent import Timeout
from agent import Message
from abc import abstractmethod
from abc import ABCMeta

import django.db
import traceback
import urllib2
import time
import gc

class WorkerIOHelper(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, params):
		django.db.close_connection()
		self.serializer = serializers.get_serializer("json")()
		self.task_iter = None
		self.deferred_tasks = deque()
		self.errors = 0
		self.error_limit = 32
		self.dropped_tasks = 0

	@property
	@abstractmethod
	def total_task(self):
		raise NotImplementedError("You should implement this method")

	def save_output(self, worker_output_json):
		worker_output = self.deserialize(worker_output_json)
		for record in worker_output:
			sid = transaction.savepoint()
			try:
				record.save()
			except Exception:
				transaction.savepoint_rollback(sid)
				print traceback.format_exc()
			else:
				transaction.savepoint_commit(sid)
		gc.collect()

	def deserialize(self, json):
		return serializers.deserialize("json", json)

	def read_next_task(self):
		if not len(self.deferred_tasks):
			for _ in xrange(0, 128):
				try:
					new_task = (self.task_iter.next(), 0)
					self.deferred_tasks.append(new_task)
				except StopIteration: break
		if len(self.deferred_tasks):
			return self.deferred_tasks.pop()
		raise StopIteration()

	def try_it_later(self, task):
		task, error_counter = task
		self.errors += 1
		if error_counter < self.error_limit:
			self.deferred_tasks.appendleft((task, error_counter + 1,))
		else:
			self.dropped_tasks += 1
			print "task droppped", task

	def cache_size(self):
		return len(self.deferred_tasks)


class Worker(AbsAgent):
	process = False

	class Status(object):
		WAIT = 0
		BUSY = 1

	def __init__(self, address, params):
		django.db.close_connection()
		self.params = params
		self.worker = None
		self.serializer = None
		super(Worker, self).__init__(address, latency=Timeout.Latency.LOW)

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
				result = self.do_work(task[0])
				self.mailbox.send(result, message.sent_from, Message.DONE)
				gc.collect()
			except Exception:
				error_str = u"task: <%s>\n%s.__handle_message__: \n%s"\
							% (str(task),
							   self.__class__.__name__,
							   traceback.format_exc())
				self.mailbox.send(error_str, message.sent_from, Message.FAIL)
				time.sleep(self.tm.current)
		else:
			error_str = u"%s.__handle_message__" \
						u"got wrongmessage type: %s %s"\
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


class TextFetcher(object):

	def __init__(self, encoding="utf-8", timeout=25):
		self.timeout = timeout
		self.encoding = encoding

	def fetch_text(self, url):
		req = urllib2.urlopen(url, timeout=self.timeout)
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