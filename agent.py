# -*- coding: utf-8 -*-

from __future__ import with_statement

import multiprocessing
import threading
import time
import pickle
import redis
import random
import worker
import logging
import traceback

from options import DATABASE_CONFIG
from abc import ABCMeta
from abc import abstractmethod

ALPHABET = "abcdefghijklmnopqrstuvwxyz"\
		   "ABCDEFGHIJKLMNOPQRSTUVWXYZ"\
		   "0123456789"#~!@#$%^&*()_+<>?"
KEY_LEN = 8

def gen_key(length=KEY_LEN, alphabet=ALPHABET):
	name = "".join(random.sample(alphabet, length))
	return name


def connection_pool():
	return redis.ConnectionPool(
		db=DATABASE_CONFIG["redis"].get("db", 0),
		port=DATABASE_CONFIG["redis"].get("port", 6379),
		host=DATABASE_CONFIG["redis"].get("host", "127.0.0.1"),
	)


class Message(object):
	REGULAR = 0
	STOP = 1
	PING = 2
	CAST = 3
	CALL = 4
	DONE = 5
	FAIL = 6

	def __init__(self, sent_from, sent_to, body, extra):
		self.sent_from = sent_from
		self.sent_to = sent_to
		self.body = body
		self.extra = extra

	@property
	def extras(self):
		return self.extra_name(self.extra)

	@staticmethod
	def extra_name(extra):
		if extra is Message.REGULAR:
			return "REGULAR"
		elif extra is Message.STOP:
			return "STOP"
		elif extra is Message.PING:
			return "PING"
		elif extra is Message.CAST:
			return "CAST"
		elif extra is Message.CALL:
			return "CALL"
		elif extra is Message.DONE:
			return "DONE"
		elif extra is Message.FAIL:
			return "FAIL"

	def dumps(self):
		return pickle.dumps(self, pickle.HIGHEST_PROTOCOL)

	@staticmethod
	def loads(string):
		return pickle.loads(string)


class MailBox(object):
	def __init__(self, address):
		self.lock = threading.RLock()
		with self.lock:
			self.sleep_min = 0.005
			self.sleep_max = 0.050
			self.sleep_koe = 1.030
			self.address = str(address)
			self.pool = connection_pool()
			self.conn = redis.Redis(connection_pool=self.pool)

	def flush(self):
		with  self.lock:
			self.conn.delete(self.address)

	def send(self, message_body, to, extra=Message.REGULAR):
		if isinstance(to, MailBox):
			to_address = to.address
		else:
			to_address = str(to)
		message = Message(self.address, to_address, message_body, extra=extra)
		packed = message.dumps()
		with self.lock:
			self.conn.lpush(to_address, packed)

	def pop_message(self):
		message = None
		with self.lock:
			packed = self.conn.rpop(self.address)
			if packed:
				message = Message.loads(packed)
		return message

	def messages(self):
		message = self.pop_message()
		while message:
			yield message
			message = self.pop_message()

	def __len__(self):
		with self.lock:
			size = self.conn.llen(self.address)
		return size

	def call(self, call_body, to):
		if isinstance(to, MailBox):
			to_address = to.address
		else:
			to_address = str(to)
		call_address = "%s-%s" % (self.address, to_address)
		message = Message(call_address, to_address, call_body,
			extra=Message.CALL)
		packed = message.dumps()
		with self.lock:
			self.conn.lpush(to_address, packed)
		with self.lock:
			response = self.conn.rpop(call_address)
		sleep = self.sleep_min
		while not response:
			time.sleep(sleep)
			with self.lock:
				response = self.conn.rpop(call_address)
			if sleep < self.sleep_max:
				sleep *= self.sleep_koe
		with self.lock:
			self.conn.delete(call_address)
		return Message.loads(response)

	def destroy(self):
		with self.lock:
			self.conn.delete(self.address)


class AbsAgent(object):
	__metaclass__ = ABCMeta

	class Latency(object):
		EXTRA_LOW = 0
		LOW = 1
		MEDIUM = 2
		HIGH = 3
		EXTRA_HIGH = 4

	def __init__(self, aid, unit_type=threading.Thread,
				 latency=Latency.MEDIUM):
		self.__aid = aid
		self.mailbox = None
		self.recv_timeout = 1
		self.sleep_min = None
		self.sleep_max = None
		self.sleep_koe = None
		self.latency = latency
		self.unit = unit_type(target=self.__message_loop, args=(self,))
		self.unit.daemon = True
		self.unit.start()

	@property
	def aid(self):
		return self.__aid

	@staticmethod
	def __message_loop(agent):
		agent.initialize()
		sleep = agent.sleep_min
		while True:
			message = agent.mailbox.pop_message()
			if message:
				sleep = agent.sleep_min
				if message.extra == message.CALL\
				or message.extra == message.CAST:
					func = getattr(agent, message.body[0])
					args = message.body[1]
					try:
						result = func(*args)
						agent.mailbox.send(result, message.sent_from,
							Message.DONE)
					except Exception:
						traceback.print_exc()
						agent.mailbox.send("", message.sent_from, Message.FAIL)
				elif message.extra == message.STOP:
					if message.sent_from is not None:
						agent.mailbox.send(("stop", "ok"), message.sent_from)
					agent.terminate()
					exit(0)
				elif message.extra == message.PING:
					agent.mailbox.send("pong", message.sent_from)
				else:
					agent.handle_message(message)
			else:
				time.sleep(sleep)
				if sleep < agent.sleep_max:
					sleep *= agent.sleep_koe

	def send(self, message_body, send_from_mb, extra=Message.REGULAR):
		send_from_mb.send(message_body, self.aid, extra)

	def stop(self, send_from_mb):
		self.send(None, send_from_mb, Message.STOP)

	def call(self, func_name, args, send_from_mb):
		message = (func_name, args)
		response = send_from_mb.call(message, self.aid)
		return response.body

	def cast(self, func_name, args, send_from_mb):
		message = (func_name, args)
		self.send(message, send_from_mb, Message.CAST)

	def initialize(self):
		self.mailbox = MailBox(self.aid)
		if self.latency is self.Latency.EXTRA_LOW:
			self.sleep_min = 0.005
			self.sleep_max = 0.050
			self.sleep_koe = 1.030
		elif self.latency is self.Latency.LOW:
			self.sleep_min = 0.010
			self.sleep_max = 0.100
			self.sleep_koe = 1.050
		elif self.latency is self.Latency.MEDIUM:
			self.sleep_min = 0.050
			self.sleep_max = 0.500
			self.sleep_koe = 1.020
		elif self.latency is self.Latency.HIGH:
			self.sleep_min = 0.100
			self.sleep_max = 1.000
			self.sleep_koe = 1.030
		elif self.latency is self.Latency.EXTRA_HIGH:
			self.sleep_min = 0.100
			self.sleep_max = 3.000
			self.sleep_koe = 1.050
		self.mailbox.sleep_min = self.sleep_min
		self.mailbox.sleep_max = self.sleep_max
		self.mailbox.sleep_koe = self.sleep_koe

	def terminate(self):
		self.mailbox.destroy()

	@abstractmethod
	def handle_message(self, message, *args, **kwargs):
		raise NotImplementedError("You should implement this method")

	def __unicode__(self):
		return u"<Agent(# %s)>" % self.aid


class AgentTracer(AbsAgent):
	def ping(self, send_from_mb):
		self.send(None, send_from_mb, Message.PING)

	def handle_message(self, message, *args, **kwargs):
		self.mailbox.send(("got", message.extras, message.body),
			message.sent_from)

	def sum(self, *args):
		return sum(args)


class Agency(AbsAgent):
	agency_address = "0"

	def __init__(self):
		self.agent_addresses = None
		self.call_back_address = gen_key()
		super(Agency, self).__init__(Agency.agency_address,
			unit_type=multiprocessing.Process, latency=self.Latency.MEDIUM)
		pool = connection_pool()
		conn = redis.Redis(connection_pool=pool)
		resp = conn.get(self.call_back_address)
		while not resp:
			time.sleep(0.1)
			resp = conn.get(self.call_back_address)
		if resp != "SUCCESS":
			logging.debug("Agency init error: %s" % resp)
			exit(1)
		else:
			conn.delete(self.call_back_address)
			pool.disconnect()

	def initialize(self):
		super(Agency, self).initialize()
		if self.mailbox.conn.dbsize() > 0:
			self.mailbox.conn.flushdb()
		self.mailbox.conn.set(self.call_back_address, "SUCCESS")
		self.agent_addresses = set()

	def _alloc_address(self):
		new_address = gen_key()
		while new_address in self.agent_addresses:
			new_address = gen_key()
		self.agent_addresses.add(new_address)
		return new_address

	def _free_address(self, address):
		self.agent_addresses.discard(address)

	def _addr_exists(self, address):
		return address in self.agent_addresses

	@staticmethod
	def _call_agency(func_name, args, send_from_mb):
		message = (func_name, args)
		response = send_from_mb.call(message, Agency.agency_address)
		return response.body

	@staticmethod
	def alloc_address(send_from_mb):
		func_name = "_alloc_address"
		return Agency._call_agency(func_name, (), send_from_mb)

	@staticmethod
	def free_address(address, send_from_mb):
		func_name = "_free_address"
		return Agency._call_agency(func_name, (address,), send_from_mb)

	@staticmethod
	def addr_exists(address, send_from_mb):
		func_name = "_addr_exists"
		return Agency._call_agency(func_name, (address,), send_from_mb)

	def handle_message(self, message, *args, **kwargs):
		pass


class AbsAgentWorker(AbsAgent):
	worker_class = worker.IWorker

	def __init__(self, aid, params):
		self.params = params
		self.worker = None
		super(AbsAgentWorker, self).__init__(aid)

	def initialize(self):
		super(AbsAgentWorker, self).initialize()
		self.init_worker(self.params)

	#	@abstractmethod
	def init_worker(self, params):
	# Put there worker initialization
	#		raise NotImplementedError("You should implement this method")
		pass

	def handle_message(self, message, *args, **kwargs):
		# Put there input data handling
		task_id = message.body["id"]
		self.mailbox.send({"id":task_id},message.sent_from, Message.DONE)


	@staticmethod
	def input_data_iter(params):
		return [1,2,3]
#		raise NotImplementedError("You should implement this method")

	@staticmethod
	def save_output_data(data, params):
		pass
		#		raise NotImplementedError("You should implement this method")

	@staticmethod
	def default_params():
		return {}