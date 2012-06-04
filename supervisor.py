# -*- coding: utf-8 -*-

import gc
import datetime
from agent import gen_key
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
		self._worker_class = worker_class
		self._worker_slots = None
		self._task_io = None
		self._params = None
		self._status = None
		self._complete_tasks = None
		self._in_process_tasks = None
		self._error_log = None
		super(AbsSupervisor, self).__init__(address,
			latency=Timeout.Latency.EXTRA_LOW)

	def __init_agent__(self):
		super(AbsSupervisor, self).__init_agent__()
		self._worker_slots = dict()
		self._error_log = deque(maxlen=32)
		self._params = self.__full_default_params__()
		self._status = ISupervisor.Status.SLEEP
		self._agent_task_frame_size = 128

	def __run_session__(self):
		if self._status is ISupervisor.Status.SLEEP\
		   or self._status is ISupervisor.Status.DONE:
			self._status = ISupervisor.Status.BUSY
			self._task_io = self._worker_class.make_task_io(self._params)
			self._complete_tasks = 0
			self.__respawn_workers__()
			self._in_process_tasks = dict()

	def __assign_next_task__(self, worker_slot):
		with self._mailbox._lock:
			if self._status is ISupervisor.Status.BUSY:
				task_frame = []
				for _ in xrange(0, self._agent_task_frame_size):
					try:
						new_task = self._task_io.read_next_task()
						task_key = gen_key()
						task_frame.append((task_key, new_task))
						self._in_process_tasks[task_key] = new_task
					except StopIteration: break
				# print "task frame size", len(task_frame)
				if task_frame:
					address = worker_slot.agent.address
					self._mailbox.send(task_frame, address, Message.TASK)
					# print "task frame send"
					worker_slot.status = Worker.Status.BUSY

	def __stop_session__(self):
		if self._status is ISupervisor.Status.BUSY:
			self.__respawn_workers__(0)
			self._status = ISupervisor.Status.SLEEP
			self._complete_tasks = 0
			self._task_io = None
			self._in_process_tasks = None
			self._error_log = deque(maxlen=32)

	def __handle_complete_task__(self, task_key, task):
		with self._mailbox._lock:
			self._task_io.save_output(task)
			self._complete_tasks += 1
			del self._in_process_tasks[task_key]

	def __handle_failed_task__(self, task_key, error_str):
		with self._mailbox._lock:
			failed_task = self._in_process_tasks[task_key]
			self._task_io.try_it_later(failed_task)
			self._error_log.append((datetime.datetime.now(), error_str))
			del self._in_process_tasks[task_key]

	def __handle_message__(self, message, *args, **kwargs):
		if self._status is ISupervisor.Status.BUSY:
			if message.extra is message.TASK:
				address = message.sent_from
				if address in self._worker_slots:
					worker = self._worker_slots[address]
					worker.status = Worker.Status.WAIT
				output_frame = message.body
				for task_key, extra, result in output_frame:
					if extra is Message.DONE:
						self.__handle_complete_task__(task_key, result)
					elif extra is message.FAIL:
						self.__handle_failed_task__(task_key, result)
			actual_task_number = self._task_io.total_tasks\
							   - self._task_io.dropped_tasks
			if self._complete_tasks == actual_task_number:
				self._status = ISupervisor.Status.DONE

	def do_periodic_things(self):
		import pickle
		self.__assign_tasks__()
		# TODO(vladimir@zvm.me): refactor this
		state = self.__get_full_state__()
		self._mailbox._conn.set("@%s" % self.address, pickle.dumps(state))

	def __assign_tasks__(self):
		if self._status is ISupervisor.Status.BUSY:
			for worker_slot in self._worker_slots.itervalues():
				if worker_slot.status is Worker.Status.WAIT:
					self.__assign_next_task__(worker_slot)

	def __respawn_workers__(self, pool_size=None):
		if pool_size is None:
			pool_size = int(self._params["common"]["pool_size"])
		while len(self._worker_slots) < pool_size:
			self.__add_worker__()
		while len(self._worker_slots) > pool_size:
			self.__rem_worker__()
		gc.collect()

	def __add_worker__(self):
		with self._mailbox._lock:
			new_address = Agency.alloc_address(self._mailbox)
			new_worker = self._worker_class(new_address, self._params)
			new_worker_slot = WorkerSlot(new_worker)
			self._worker_slots[new_address] = new_worker_slot

	def __rem_worker__(self):
		while True:
			for slot in self._worker_slots.itervalues():
				if slot.status is Worker.Status.WAIT:
					slot.agent.stop(self._mailbox)
					address = slot.agent.address
					Agency.free_address(address, self._mailbox)
					with self._mailbox._lock:
						del(self._worker_slots[address])
					return
			for slot in self._worker_slots.itervalues():
				slot.agent.stop(self._mailbox)
				address = slot.agent.address
				Agency.free_address(address, self._mailbox)
				with self._mailbox._lock:
					del(self._worker_slots[address])
				return

	def __busy_workers__(self):
		active = 0
		for slot in self._worker_slots.itervalues():
			if slot.status is Worker.Status.BUSY:
				active += 1
		return active

	def __clear_log__(self):
		self._error_log = deque(maxlen=32)

	def __set_pool_size__(self, new_size):
		self._params["common"]["pool_size"] = int(new_size)
		self.__respawn_workers__()

	def __get_full_state__(self):
		common, specific = self.__get_state__()
		state = OrderedDict((
			("common", OrderedDict((
				("address", self.address),
				("name", self.name),
				("pool_size", len(self._worker_slots)),
				("status", ISupervisor.Status.name(self._status)),
				("complete_percentage", self.__complete_percentage__()),
				("total_tasks",
					self._task_io.total_tasks if self._task_io else 0),
				("complete_tasks",
					self._complete_tasks if self._complete_tasks else 0),
				("params", self._params),
				("active_workers",self.__busy_workers__()),
				("error_log", print_log(self._error_log)),
				("errors_occurred", 
					self._task_io.errors if self._task_io else 0),
				("dropped_tasks",
					self._task_io.dropped_tasks if self._task_io else 0),
				("cached_tasks",
					self._task_io.cache_size() if self._task_io else 0),
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
			self._params[section][key] = new_value
			return new_value
		except Exception: return None

	def __complete_percentage__(self):
		if self._task_io and self._complete_tasks:
			return float(self._complete_tasks)\
				   / float(self._task_io.total_tasks)\
				   * 100.0
		return 0



def print_log(log):
	from itertools import imap
	return u"\n".join(imap(lambda x: x[1], log))



def read_supv_state(mailbox, supv):
	import pickle
	state = mailbox.conn.get("@%s" % supv.address)
	if state:
		return pickle.loads(state)
	return None