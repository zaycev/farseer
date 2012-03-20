# -*- coding: utf-8 -*-
import time

from agent import AbsAgent
from agent import Agency
from worker import IWorker

from abc import ABCMeta
from abc import abstractmethod
from collections import OrderedDict

import multiprocessing

class ISupervisor(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def add_worker(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def rem_worker(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def default_params(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __default_params__(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def get_state(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __get_state__(self):
		raise NotImplementedError("You should implement this method")

class AbsSupervisor(AbsAgent, ISupervisor):

	@abstractmethod
	def __init__(self, aid, worker_cls):
		self.worker_cls = worker_cls
		self.workers = None
		self.input_queue = None
		self.output_queue = None
		self.pool_size = 2
		self.params = None
		super(AbsSupervisor, self).__init__(aid,
			unit_type=multiprocessing.Process)

	def initialize(self):
		super(AbsSupervisor, self).initialize()
		self.workers = dict()
		self.input_queue = []
		self.output_queue = []

	def run(self):
		raise NotImplementedError("You should implement this method")

	def add_worker(self):
		with self.mailbox.lock:
			new_address = Agency.alloc_address(self.mailbox)
			new_worker = self.worker_cls(new_address, self.params)
			self.workers[new_address] = (new_worker, IWorker.State.WAIT)

	def rem_worker(self):
		with self.mailbox.lock:
			while True:
				for worker, status in self.workers:
					if status is IWorker.State.WAIT:
						worker.stop(self.mailbox)
						address = worker.aid
						Agency.free_address(address, self.mailbox)
						return
				time.sleep(0.5)


	def handle_message(self, message, *args, **kwargs):
		print "Do some task"

	def __get_state__(self):
		return {}

	def get_state(self):
		return {
			"extra": OrderedDict(self.__get_state__()),
			"common": dict([
				("name", self.__class__.__name__),
				("pool_size", len(self.workers)),
				("status", self.status),
				("job_done", self.job_done),
				("address", self.aid),
			]),
		}

	@property
	def job_done(self):
		return 12

	def __default_params__(self):
		return []

	@property
	def status(self):
		if self.workers:
			if all([s is IWorker.State.BUSY for w,s in self.workers]):
				return "waiting"
			return "busy"
		return "sleep"


	def default_params(self):
		return {
			"superv": OrderedDict(self.__default_params__()),
			"worker": OrderedDict(self.worker_cls.default_parsms()),
		}