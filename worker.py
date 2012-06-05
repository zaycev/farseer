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
import gc



class TaskIO(object):
	"""
	TaskIO helps worker to read and write data input and output data.
	"""
	__metaclass__ = ABCMeta
	@property
	@abstractmethod
	def total_tasks(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __init__(self, params):
		django.db.close_connection()
		self._serializer = serializers.get_serializer("json")()
		self._task_iter = None
		self._deferred_tasks = deque()
		self._errors = 0
		self._error_limit = 32
		self._dropped_tasks = 0

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
		django.db.reset_queries()
		gc.collect()

	def deserialize(self, json):
		return serializers.deserialize("json", json)

	def read_next_task(self):
		if not len(self._deferred_tasks):
			for _ in xrange(0, 1024):
				try:
					new_task = (self._task_iter.next(), 0)
					self._deferred_tasks.append(new_task)
				except StopIteration: pass
		if len(self._deferred_tasks):
			return self._deferred_tasks.pop()
		raise StopIteration()

	def try_it_later(self, task):
		task, error_counter = task
		self._errors += 1
		if error_counter < self._error_limit:
			self._deferred_tasks.appendleft((task, error_counter + 1,))
		else:
			self._dropped_tasks += 1

	def cache_size(self):
		return len(self._deferred_tasks)



class TestIOHelper(TaskIO):
	@property
	def total_tasks(self):
		return self.tasks_count

	def __init__(self, params):
		super(TestIOHelper, self).__init__(params)
		self.tasks_count = params.get("tasks_count", 100)
		self._task_iter = xrange(0, self.tasks_count).__iter__()



class Worker(AbsAgent):
	process = False

	class Status(object):
		WAIT = 0
		BUSY = 1

	def __init__(self, address, params):
		django.db.close_connection()
		self._params = params
		self._serializer = None
		super(Worker, self).__init__(address, latency=Timeout.Latency.LOW)

	def __init_agent__(self):
		super(Worker, self).__init_agent__()
		with self._mailbox._lock:
			self._serializer = serializers.get_serializer("json")()
			self.__init_worker__(self._params)
			self._params = None

	def __init_worker__(self, params):
		pass

	def __handle_message__(self, message, *args, **kwargs):
		if message.msg_type is Message.TASK:
			task_frame = message.body
			output_frame = []
			for task_key, task in task_frame:
				try:
					result = self.do_work(task[0])
					output_frame.append((task_key, Message.DONE, result))
					gc.collect()
				except Exception:
					print traceback.format_exc()
					error_str = u"task: <%s>\n%s.__handle_message__: \n%s"\
								% (str(task),
								   self.__class__.__name__,
								   traceback.format_exc())
					output_frame.append((task_key, Message.FAIL, error_str))
			self._mailbox.send(output_frame, message.sent_from, Message.TASK)
		else:
			error_str = u"%s.__handle_message__" \
						u"got wrong message type: <%s> %s"\
						% (self.__class__.__name__,
						   message.msg_type,
						   message.msg_types)
			self._mailbox.send(error_str, message.sent_from, Message.FAIL)

	def do_work(self, task):
		pass

	def __is_free__(self):
		return True

	@staticmethod
	def make_task_io(params):
		raise NotImplementedError("You should implement this method")



class TestWorker(Worker):

	def __init_worker__(self, params):
		self.increment = params["increment"]

	def do_work(self, task):
		import fortest.models
		result = fortest.models.MockModel(
			task = task,
			result = task + self.increment)
		logging.debug(
			"tasks left %s" %
			self._mailbox._conn.llen(self._mailbox.address))
		return self._serializer.serialize([result])

	@staticmethod
	def make_task_io(params):
		return TestIOHelper(params)