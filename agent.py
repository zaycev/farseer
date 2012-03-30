# -*- coding: utf-8 -*-

from __future__ import with_statement

import multiprocessing
import threading
import time
import pickle
import redis
import random
import logging
import traceback

from options import DATABASE_CONFIG
from abc import ABCMeta
from abc import abstractmethod


ALPHABET = "abcdefghijklmnopqrstuvwxyz"\
		   "ABCDEFGHIJKLMNOPQRSTUVWXYZ"\
		   "0123456789"
AGENCY_WRAPPER = None

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


class Timeout(object):

	class Latency:
		EXTRA_LOW = 0
		LOW = 1
		MEDIUM = 2
		HIGH = 3
		EXTRA_HIGH = 4

	def __init__(self, initial=0.050, max=0.200, k=1.050, max_iter=None):
		self.initial = initial
		self.max = max
		self.k = k
		self.max_iter = max_iter
		self.current = None
		self.current_i = None

	def reset(self):
		self.current = self.initial
		self.current_i = 0

	def set_latency(self, latency):
		if latency is self.Latency.EXTRA_LOW:
			self.initial = 0.015
			self.max = 0.120
			self.k = 1.030
		elif latency is self.Latency.LOW:
			self.initial = 0.050
			self.max = 0.200
			self.k = 1.050
		elif latency is self.Latency.MEDIUM:
			self.initial = 0.100
			self.max = 0.500
			self.k = 1.020
		elif latency is self.Latency.HIGH:
			self.initial = 0.200
			self.max = .800
			self.k = 1.030
		elif latency is self.Latency.EXTRA_HIGH:
			self.initial = 0.200
			self.max = 3.000
			self.k = 1.050

	def __iter__(self):
		self.reset()
		while self.current_i < self.max_iter or not self.max_iter:
			yield self.current
			if self.current < self.max:
				self.current *= self.k
			self.current_i += 1
		raise StopIteration()

class MailBoxException(Exception):
	pass

class Message(object):
	REGULAR = 0
	STOP = 1
	PING = 2
	CAST = 3
	CALL = 4
	DONE = 5
	FAIL = 6
	TASK = 7

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
		elif extra is Message.TASK:
			return "TASK"

	def dumps(self):
		return pickle.dumps(self, pickle.HIGHEST_PROTOCOL)

	@staticmethod
	def loads(string):
		return pickle.loads(string)


class MailBox(object):
	def __init__(self, address, latency=Timeout.Latency.EXTRA_LOW):
		self.lock = threading.RLock()
		with self.lock:
			self.address = str(address)
			self.pool = connection_pool()
			self.conn = redis.StrictRedis(connection_pool=self.pool)
			self.tm = Timeout(max_iter=1024)
			self.tm.set_latency(latency)

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
			#print "try lpush %s" % to_address
			self.conn.lpush(to_address, packed)
			#print "ok, lpushed"

	def pop_message(self):
		with self.lock:
			if self.conn.llen(self.address) > 0:
				packed = self.conn.rpop(self.address)
				return Message.loads(packed)
		return None

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
		response = None
		with self.lock:
			self.conn.lpush(to_address, packed)
		for t in self.tm:
			with self.lock:
				response = self.conn.rpop(call_address)
			if response: break
			time.sleep(t)
		with self.lock:
			self.conn.delete(call_address)
		if response:
			return Message.loads(response)
		raise MailBoxException("Timeout %s exceeded" % self.address)

	def destroy(self):
		with self.lock:
			self.conn.delete(self.address)


class AbsAgent(object):
	__metaclass__ = ABCMeta
	process = True

	def __init__(self, address,latency=Timeout.Latency.MEDIUM):
		self.__address = address
		self.latency = latency
		if self.process:
			self.unit = multiprocessing\
				.Process(target=self.__message_loop__, args=(self,))
		else:
			self.unit = threading\
				.Thread(target=self.__message_loop__, args=(self,))
#		self.unit.daemon = True
		self.unit.start()

	def __init_agent__(self):
		self.mailbox = MailBox(self.address, self.latency)
		self.tm = Timeout()
		self.tm.set_latency(self.latency)

	@property
	def address(self):
		return self.__address

	@staticmethod
	def __message_loop__(agent):
		agent.__init_agent__()
		for t in agent.tm:
			message = agent.mailbox.pop_message()
			if message:
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
						agent.__stop__()
				elif message.extra == message.PING:
					agent.mailbox.send("pong", message.sent_from)
				else:
					agent.__handle_message__(message)
				agent.tm.reset()
			else:
				time.sleep(t)
				#print "sleep"
			agent.do_periodic_things()

	def do_periodic_things(self):
		pass

	def send(self, message_body, send_from_mb, extra=Message.REGULAR):
		send_from_mb.send(message_body, self.address, extra)

	def __stop__(self):
		self.terminate()
		exit(0)

	def stop(self, send_from_mb):
		self.send(None, send_from_mb, Message.STOP)

	def call(self, func_name, args, send_from_mb):
		message = (func_name, args)
		response = send_from_mb.call(message, self.address)
		return response.body

	def cast(self, func_name, args, send_from_mb):
		message = (func_name, args)
		self.send(message, send_from_mb, Message.CAST)

	def terminate(self):
		self.mailbox.destroy()

	@abstractmethod
	def __handle_message__(self, message, *args, **kwargs):
		raise NotImplementedError("You should implement this method")

	def __unicode__(self):
		return u"<Agent(# %s)>" % self.address


class AgentTracer(AbsAgent):
	def ping(self, send_from_mb):
		self.send(None, send_from_mb, Message.PING)

	def __handle_message__(self, message, *args, **kwargs):
		self.mailbox.send(("got", message.extras, message.body),
			message.sent_from)

	def sum(self, *args):
		return sum(args)


class Agency(AbsAgent):
	process = True
	agency_address = "0"

	def __init__(self):
		self.agent_addresses = None
		self.call_back_address = gen_key()
		super(Agency, self).__init__(Agency.agency_address, latency=Timeout.Latency.EXTRA_LOW)
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

	def __init_agent__(self):
		super(Agency, self).__init_agent__()
		if self.mailbox.conn.dbsize() > 0:
			self.mailbox.conn.flushdb()
		self.mailbox.conn.set(self.call_back_address, "SUCCESS")
		self.agent_addresses = set()
		self.counter = 1000

	def _alloc_address(self):
		new_address = str(self.counter)
		self.agent_addresses.add(new_address)
		self.counter += 1
		return new_address

	def _free_address(self, address):
		self.agent_addresses.discard(address)
		return address

	def _addr_exists(self, address):
		return address in self.agent_addresses

	@staticmethod
	def _send_agency(message_body, send_from_mb, extra=Message.REGULAR):
		send_from_mb.send(message_body, Agency.agency_address, extra)

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

	@staticmethod
	def stop_all(send_from_mb):
		Agency._send_agency(None, send_from_mb, extra=Message.STOP)

	def __handle_message__(self, message, *args, **kwargs):
		pass

	def terminate(self):
		logging.debug("AGENCY TERMINATED")
		for address in self.agent_addresses:
			self.mailbox.send(None, address, Message.STOP)
		self.mailbox.destroy()


class AgencyWrapper(object):

	def __init__(self):
		Agency()
		self.mb = MailBox("master")

	def alloc_address(self):
		return Agency.alloc_address(self.mb)

	def free_address(self, address):
		return Agency.free_address(address, self.mb)

	def addr_exists(self, address):
		return Agency.addr_exists(address, self.mb)

	def stop_all(self):
		global AGENCY_WRAPPER
		AGENCY_WRAPPER = None
		Agency.stop_all(self.mb)


def create_agency():
	global AGENCY_WRAPPER
	if not AGENCY_WRAPPER:
		AGENCY_WRAPPER = AgencyWrapper()
	return AGENCY_WRAPPER