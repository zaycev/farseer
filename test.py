#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from manage import setup_environment
import imp
try:
	imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
	import sys
	sys.stderr.write("Error: Can't find the file 'settings.py'"
					"in the directory containing %r. It appears"
					" you've customized things.\nYou'll have to"
					" run django-admin.py, passing it your "
					"settings module.\n" % __file__)
	sys.exit(1)

import time
import agent
import logging

from agent import Message
from agent import MailBox
from agent import AgentTracer
from agent import create_agency, AgencyWrapper

from worker import TestIOHelper
from worker import TestWorker

TERMINATING_TIMEOUT = 0.3

class AgencyTest(unittest.TestCase):

	def test_agency_wrapper(self):
		self.assertIsNone(agent.AGENCY_WRAPPER)

		agency = create_agency()
		self.assertIsInstance(agency, AgencyWrapper)
		agency.stop_all()

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)

	def test_address(self):
		self.assertIsNone(agent.AGENCY_WRAPPER)

		agency = create_agency()
		addresses = [agency.alloc_address() for _ in xrange(0, 8)]
		exists = [agency.addr_exists(addr) for addr in addresses]
		for addr in addresses:
			agency.free_address(addr)
		doesnt_exists = [agency.addr_exists(addr) for addr in addresses]
		self.assertTrue(all(exists))
		self.assertFalse(any(doesnt_exists))

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)

class MessageTest(unittest.TestCase):

	def test_init(self):
		self.assertIsNone(agent.AGENCY_WRAPPER)

		agency = create_agency()
		a1 = agency.alloc_address()
		a2 = agency.alloc_address()
		body = "test body"
		msg = Message(a1, a2, body,
			Message.PING)
		self.assertIsNotNone(msg)
		self.assertEquals(msg.sent_from, a1)
		self.assertEquals(msg.sent_to, a2)
		self.assertEquals(msg.body, body)
		self.assertEquals(msg.msg_type, Message.PING)

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)

class MailBoxTest(unittest.TestCase):

	def test_init(self):
		self.assertIsNone(agent.AGENCY_WRAPPER)

		agency = create_agency()
		mb = MailBox(agency.alloc_address())
		self.assertIsNotNone(mb)
		for _ in xrange(0, 100):
			m = MailBox(agency.alloc_address())
			self.assertIsNotNone(m)

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)

	def test_send(self):
		agency = create_agency()

		a1 = agency.alloc_address()
		a2 = agency.alloc_address()
		body = "I'm Lrrr, ruler of the planet Omicron Persei 8"
		mb1 = MailBox(a1)
		mb2 = MailBox(a2)
		mb1.send(body, mb2, Message.REGULAR)
		time.sleep(0.1)
		received_message = mb2.pop_message()
		self.assertEqual(received_message.sent_from, mb1.address)
		self.assertEqual(received_message.sent_to, mb2.address)
		self.assertEqual(received_message.body, body)
		self.assertEqual(received_message.extra, Message.REGULAR)
		mb1.destroy()
		mb2.destroy()

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)

	def test_messages(self):
		self.assertIsNone(agent.AGENCY_WRAPPER)

		agency = create_agency()
		a1 = agency.alloc_address()
		a2 = agency.alloc_address()
		mb1 = MailBox(a1)
		mb2 = MailBox(a2)
		msg_bodies = [1,2,3,4,5,"Hello",[1,2,0.2], {"key":1, "value":2}]
		for body in msg_bodies:
			mb1.send(body, mb2)
		time.sleep(0.5)
		received_bodies = [msg.body for msg in mb2.messages()]
		self.assertEqual(msg_bodies, received_bodies)
		mb1.destroy()
		mb2.destroy()

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)


class AgentTracerTest(unittest.TestCase):

	def test_init(self):
		self.assertIsNone(agent.AGENCY_WRAPPER)

		agency = create_agency()
		a1 = agency.alloc_address()
		a2 = agency.alloc_address()
		a = AgentTracer(a1)
		mb = MailBox(a2)
		body = ("some generic text", 1, {1,2,3}, {"a":1, "b":[0.1,-1]},)
		time.sleep(0.5)
		self.assertIsNotNone(a)
		self.assertIsNotNone(a.address, a1)
		a.send(body, mb)
		a.ping(mb)
		a.stop(mb)
		time.sleep(0.5)
		received_messages = list(mb.messages())
		self.assertEqual(received_messages[0].body,
			("got", Message.msg_type_name(Message.REGULAR), body))
		self.assertEqual(received_messages[1].body, "pong")
		self.assertEqual(received_messages[2].body, ("stop", "ok"))
		self.assertFalse(a._unit.is_alive())
		mb.destroy()

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)


	def test_call(self):
		self.assertIsNone(agent.AGENCY_WRAPPER)

		agency = create_agency()
		ags = [AgentTracer(agency.alloc_address()) for _ in xrange(0, 16)]
		m = MailBox(agency.alloc_address())
		numbers = (1,2,3,1,123123,0.3,123987127863,0.1,-1,0)
		result = [a.call("sum", numbers, m) for a in ags]
		should_be = [sum(numbers)] * len(ags)
		for a in ags:
			a.stop(m)
		self.assertEqual(result, should_be)
		m.destroy()

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)


class WorkerTest(unittest.TestCase):

	def test_io_helper(self):

		io_helper_1 = TestIOHelper({"tasks_count": 1000})
		io_helper_2 = TestIOHelper({"tasks_count": 1})

		self.assertIsInstance(io_helper_1, TestIOHelper)
		self.assertIsInstance(io_helper_2, TestIOHelper)

		self.assertEqual(io_helper_1.total_tasks, 1000)
		self.assertEqual(io_helper_2.total_tasks, 1)

		for x in xrange(0, 1000):
			self.assertEqual(0, io_helper_1.read_next_task()[1])

		for x in xrange(0, 1):
			self.assertEqual(0, io_helper_2.read_next_task()[1])

		try:
			io_helper_1.read_next_task()
			self.assertTrue(False)
		except StopIteration:
			self.assertTrue(True)

		try:
			io_helper_2.read_next_task()
			self.assertTrue(False)
		except StopIteration:
			self.assertTrue(True)

		some_task = ("SOME TASK", 0)

		io_helper_1.try_it_later(some_task)

		some_task = io_helper_1.read_next_task()

		self.assertEqual(1, some_task[1])

		another_task = ("ANOTHER TASK", 0)

		for x in range(0, io_helper_1._error_limit):
			self.assertEqual(x, another_task[1])
			io_helper_1.try_it_later(another_task)
			another_task = io_helper_1.read_next_task()

		io_helper_1.try_it_later(another_task)

		try:
			io_helper_1.read_next_task()
			self.assertTrue(False)
		except StopIteration:
			self.assertTrue(True)


	def test_do_work(self):

		self.assertIsNone(agent.AGENCY_WRAPPER)
		T_COUNT = 512
		agency = create_agency()
		params = {"tasks_count": T_COUNT, "increment": 10,}
		mb = MailBox(agency.alloc_address())
		w_address = agency.alloc_address()
		helper = TestWorker.make_task_io(params)
		for _ in xrange(0, T_COUNT):
			t = helper.read_next_task()
			#logging.debug("sent %s" % str(t))
			mb.send(t, w_address, Message.TASK)
		w = TestWorker(w_address, params)
		T_HANDLED = 0
		while T_HANDLED != T_COUNT:
			if mb._conn.llen(mb.address) > 0:
				result = mb.pop_message()
				T_HANDLED += 1
				dresult = helper.deserialize(result.body).next()
				#logging.debug("done %s %s %s"
				#	% (str(T_HANDLED), dresult, result.body))
			else:
				time.sleep(0.1)
		w.stop(mb)

		agency.stop_all()
		time.sleep(TERMINATING_TIMEOUT)
		self.assertIsNone(agent.AGENCY_WRAPPER)

	def do_work_times(self):
		for _ in xrange(0, 10):
			self.test_do_work()

#from collector.test import *
#from bundle.test import *
#from analyzer.test import *

if __name__ == "__main__":
	setup_environment()
	unittest.main()