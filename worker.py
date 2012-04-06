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
import logging
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
	def total_tasks(self):
		raise NotImplementedError("You should implement this method")

	def save_output(self, worker_output_json):
		worker_output = self.deserialize(worker_output_json)
		# print worker_output_json
		for record in worker_output:
			sid = transaction.savepoint()
			try:
				record.save()
			except Exception:
				transaction.savepoint_rollback(sid)
				print traceback.format_exc()
			else:
				transaction.savepoint_commit(sid)
		django.db.reset_queries()
		gc.collect()

	def deserialize(self, json):
		return serializers.deserialize("json", json)

	def read_next_task(self):
		if not len(self.deferred_tasks):
			for _ in xrange(0, 1024):
				try:
					new_task = (self.task_iter.next(), 0)
					self.deferred_tasks.append(new_task)
				except StopIteration: pass
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
			#print "task droppped", task

	def cache_size(self):
		return len(self.deferred_tasks)


class TestIOHelper(WorkerIOHelper):

	def __init__(self, params):
		super(TestIOHelper, self).__init__(params)
		self.tasks_count = params.get("tasks_count", 100)
		self.task_iter = xrange(0, self.tasks_count).__iter__()


	@property
	def total_tasks(self):
		return self.tasks_count

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
		with self.mailbox.lock:
			self.serializer = serializers.get_serializer("json")()
			self.__init_worker__(self.params)
			self.params = None

	def __init_worker__(self, params):
		pass

	def __handle_message__(self, message, *args, **kwargs):
		if message.extra is Message.TASK:
			task_frame = message.body
			output_frame = []
			# print "got frame", len(task_frame)
			for task_key, task in task_frame:
				try:
					result = self.do_work(task[0])
					#print "work done"
					output_frame.append((task_key, Message.DONE, result))
					gc.collect()
					#print "message sent"
				except Exception:
					#print "error occured"
					print traceback.format_exc()
					error_str = u"task: <%s>\n%s.__handle_message__: \n%s"\
								% (str(task),
								   self.__class__.__name__,
								   traceback.format_exc())
					output_frame.append((task_key, Message.FAIL, error_str))
			self.mailbox.send(output_frame, message.sent_from, Message.TASK)
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


class TestWorker(Worker):

	def __init_worker__(self, params):
		self.increment = params["increment"]

	def do_work(self, task):
		import fortest.models
		result = fortest.models.MockModel(
			task = task,
			result = task + self.increment
		)
		logging.debug(
			"tasks left %s" %
			self.mailbox.conn.llen(self.mailbox.address)
		)
		return self.serializer.serialize([result])

	@staticmethod
	def make_io_helper(params):
		return TestIOHelper(params)



class TextFetcher(object):

	def __init__(self, encoding="utf-8", timeout=25):
		self.timeout = timeout
		self.encoding = encoding

	def fetch_text(self, url):
		#print "openning url"
		#print url
		req = urllib2.urlopen("http://google.com")
		#print "detect encoding"
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
		#print "detected", encoding
		#print "try read url"
		return unicode(req.read(), encoding)