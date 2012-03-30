# -*- coding: utf-8 -*-

import gc
import datetime

from agent import Timeout
from agent import Message
from agent import AbsAgent
from agent import Agency
from worker import Worker

from abc import ABCMeta
from abc import abstractmethod
from collections import deque
from collections import OrderedDict

class WorkerSlot(object):

	def __init__(self, agent_worker):
		self.agent = agent_worker
		self.status = Worker.Status.WAIT


class ISupervisor(object):
	__metaclass__ = ABCMeta
	name = "Default Supervisor"

	class Status:
		SLEEP = 0
		BUSY = 1
		WAIT = 2
		DONE = 3

		@staticmethod
		def name(status):
			if status is ISupervisor.Status.SLEEP:
				return "SLEEP"
			elif status is ISupervisor.Status.BUSY:
				return "BUSY"
			elif status is ISupervisor.Status.WAIT:
				return "WAIT"
			elif status is ISupervisor.Status.DONE:
				return "DONE"
			return "UNKNOWN"

	@abstractmethod
	def __set_pool_size__(self, new_size):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __add_worker__(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __rem_worker__(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __complete_percentage__(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __get_state__(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __get_full_state__(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __full_default_params__(self):
		raise NotImplementedError("You should implement this method")

	@abstractmethod
	def __default_params__(self):
		raise NotImplementedError("You should implement this method")


class AbsSupervisor(AbsAgent, ISupervisor):
	process = True

	@abstractmethod
	def __init__(self, address, worker_class):
		self.worker_class = worker_class
		self.worker_slots = None
		self.io_helper = None
		self.params = None
		self.status = None
		self.complete_tasks = None
		self.sent_tasks = None
		self.error_log = None
		super(AbsSupervisor, self).__init__(address,
			latency=Timeout.Latency.EXTRA_LOW)

	def __init_agent__(self):
		super(AbsSupervisor, self).__init_agent__()
		self.worker_slots = dict()
		self.error_log = deque(maxlen=32)
		self.params = self.__full_default_params__()
		self.status = ISupervisor.Status.SLEEP

	def __run_session__(self):
		if self.status is ISupervisor.Status.SLEEP\
		   or self.status is ISupervisor.Status.DONE:
			self.status = ISupervisor.Status.BUSY
			self.io_helper = self.worker_class.make_io_helper(self.params)
			self.complete_tasks = 0
			self.__respawn_workers__()
			self.sent_tasks = dict()

	def __assign_next_task__(self, worker_slot):
		if self.status is ISupervisor.Status.BUSY:
			next_task = None
			try:
				next_task = self.io_helper.read_next_task()
			except StopIteration: pass
			if next_task:
				address = worker_slot.agent.address
				self.mailbox.send(next_task, address, Message.TASK)
				worker_slot.status = Worker.Status.BUSY
				self.sent_tasks[address] = next_task

	def __stop_session__(self):
		if self.status is ISupervisor.Status.BUSY:
			self.__respawn_workers__(0)
			self.status = ISupervisor.Status.SLEEP
			self.complete_tasks = 0
			self.io_helper = None
			self.sent_tasks = None
			self.error_log = deque(maxlen=32)

	def __handle_message__(self, message, *args, **kwargs):
		print "handle", message
		if self.status is ISupervisor.Status.BUSY:
			if message.extra is message.DONE:
				self.complete_tasks += 1
				worker_output = message.body
				with self.mailbox.lock:
					self.io_helper.save_output(worker_output)
				address = message.sent_from
				del self.sent_tasks[address]
				if address in self.worker_slots:
					worker = self.worker_slots[address]
					worker.status = Worker.Status.WAIT
			elif message.extra is message.FAIL:
				address = message.sent_from
				worker_last_task = self.sent_tasks[address]
				self.io_helper.try_it_later(worker_last_task)
				del self.sent_tasks[address]
				if address in self.worker_slots:
					worker = self.worker_slots[address]
					worker.status = Worker.Status.WAIT
				self.error_log.append((datetime.datetime.now(), message.body))
			if self.complete_tasks == self.io_helper.total_tasks -\
									  self.io_helper.dropped_tasks:
				self.status = ISupervisor.Status.DONE

	def do_periodic_things(self):
		self.__assing_tasks__()

	def __assing_tasks__(self):
		if self.status is ISupervisor.Status.BUSY:
			for worker_slot in self.worker_slots.itervalues():
				if worker_slot.status is Worker.Status.WAIT:
					self.__assign_next_task__(worker_slot)

	def __respawn_workers__(self, pool_size=None):
		if pool_size is None:
			pool_size = int(self.params["common"]["pool_size"])
		while len(self.worker_slots) < pool_size:
			self.__add_worker__()
		while len(self.worker_slots) > pool_size:
			self.__rem_worker__()
		gc.collect()

	def __add_worker__(self):
		with self.mailbox.lock:
			new_address = Agency.alloc_address(self.mailbox)
			new_worker = self.worker_class(new_address, self.params)
			new_worker_slot = WorkerSlot(new_worker)
			self.worker_slots[new_address] = new_worker_slot

	def __rem_worker__(self):
		while True:
			for slot in self.worker_slots.itervalues():
				if slot.status is Worker.Status.WAIT:
					slot.agent.stop(self.mailbox)
					address = slot.agent.address
					Agency.free_address(address, self.mailbox)
					with self.mailbox.lock:
						del(self.worker_slots[address])
					return
			for slot in self.worker_slots.itervalues():
				slot.agent.stop(self.mailbox)
				address = slot.agent.address
				Agency.free_address(address, self.mailbox)
				with self.mailbox.lock:
					del(self.worker_slots[address])
				return

	def __active_workers__(self):
		active = 0
		for slot in self.worker_slots.itervalues():
			if slot.status is Worker.Status.BUSY:
				active += 1
		return active

	def __clear_log__(self):
		self.error_log = deque(maxlen=32)

	def __set_pool_size__(self, new_size):
		self.params["common"]["pool_size"] = int(new_size)
		self.__respawn_workers__()

	def __get_full_state__(self):
		common, specific = self.__get_state__()
		state = OrderedDict((
			("common", OrderedDict((
				("address", self.address),
				("name", self.name),
				("pool_size", len(self.worker_slots)),
				("status", ISupervisor.Status.name(self.status)),
				("complete_percentage", self.__complete_percentage__()),
				("total_tasks", self.io_helper.total_tasks if self.io_helper else 0),
				("complete_tasks", self.complete_tasks if self.complete_tasks else 0),
				("params", self.params),
				("active_workers", self.__active_workers__()),
				("error_log", print_log(self.error_log)),
				("errors_occurred", self.io_helper.errors if self.io_helper else 0),
				("dropped_tasks", self.io_helper.dropped_tasks if self.io_helper else 0),
				("cached_tasks", self.io_helper.cache_size() if self.io_helper else 0),
			))),
			("specific", OrderedDict(specific)),
		))
		for key, value in common:
			state["common"][key] = value
		return state

	def __get_state__(self):
		return (),()

	def __full_default_params__(self):
		common, specific = self.__default_params__()
		params = OrderedDict((
			("common", OrderedDict((
				("pool_size", 1),
			))),
			("specific", OrderedDict(specific)),
		))
		for key, value in common:
			params["common"][key] = value
		return params

	def __default_params__(self):
		return (),()

	def __set_param__(self, section, key, new_value):
		try:
			self.params[section][key] = new_value
			return new_value
		except Exception: return None

	def __complete_percentage__(self):
		if self.io_helper and self.complete_tasks:
			return float(self.complete_tasks)\
				   / float(self.io_helper.total_tasks)\
				   * 100.0
		return 0


def print_log(log):
	from itertools import imap
	return u"\n".join(imap(lambda x: x[1], log))
