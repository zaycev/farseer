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
	sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
	sys.exit(1)

import time
import threading
import multiprocessing

from agent import Message
from agent import MailBox
from agent import AgentTracer
from agent import Agency

MAILBOX_ADDRESS_1 = "2424 Fulton, Berkeley CA, USA"
MAILBOX_ADDRESS_2 = "Omicron Persei 8"
class MessageTest(unittest.TestCase):

	def test_init(self):
		body = "some body"
		msg = Message(MAILBOX_ADDRESS_1, MAILBOX_ADDRESS_2, body,
			Message.PING)
		self.assertIsNotNone(msg)
		self.assertEquals(msg.sent_from, MAILBOX_ADDRESS_1)
		self.assertEquals(msg.sent_to, MAILBOX_ADDRESS_2)
		self.assertEquals(msg.body, body)
		self.assertEquals(msg.extra, Message.PING)


class MailBoxTest(unittest.TestCase):

	def test_init(self):
		mb = MailBox(MAILBOX_ADDRESS_1)
		self.assertIsNotNone(mb)

	def test_send(self):
		body = "I'm Lrrr, ruler of the planet Omicron Persei 8"
		mb1 = MailBox(MAILBOX_ADDRESS_1)
		mb2 = MailBox(MAILBOX_ADDRESS_2)
		mb1.send(body, mb2, Message.REGULAR)
		time.sleep(0.1)
		received_message = mb2.pop_message()
		self.assertEqual(received_message.sent_from, mb1.address)
		self.assertEqual(received_message.sent_to, mb2.address)
		self.assertEqual(received_message.body, body)
		self.assertEqual(received_message.extra, Message.REGULAR)
		mb1.destroy()
		mb2.destroy()

	def test_messages(self):
		mb1 = MailBox(MAILBOX_ADDRESS_1)
		mb2 = MailBox(MAILBOX_ADDRESS_2)
		msg_bodies = [1,2,3,4,5,"Hello",[1,2,0.2], {"key":1, "value":2}]
		for body in msg_bodies:
			mb1.send(body, mb2)
		time.sleep(0.1)
		received_bodies = [msg.body for msg in mb2.messages()]
		self.assertEqual(msg_bodies, received_bodies)
		mb1.destroy()
		mb2.destroy()


class AgentTracerTest(unittest.TestCase):

	def test_init(self):
		a = AgentTracer(MAILBOX_ADDRESS_1)
		mb = MailBox(MAILBOX_ADDRESS_2)
		body = ("some generic text", 1, {1,2,3}, {"a":1, "b":[0.1,-1]},)
		time.sleep(1)
		self.assertIsNotNone(a)
		self.assertIsNotNone(a.aid, MAILBOX_ADDRESS_1)
		a.send(body, mb)
		a.ping(mb)
		a.stop(mb)
		time.sleep(1)
		received_messages = list(mb.messages())
		self.assertEqual(received_messages[0].body,
			("got", Message.extra_name(Message.REGULAR), body))
		self.assertEqual(received_messages[1].body, "pong")
		self.assertEqual(received_messages[2].body, ("stop", "ok"))
		self.assertFalse(a.unit.is_alive())
		mb.destroy()

	def test_tcall(self):
		ags = [AgentTracer("agent#%s" % x, threading.Thread,
			latency=AgentTracer.Latency.EXTRA_LOW)
			   for x in xrange(0, 16)]
		m = MailBox("agency mailbox")
		numbers = (1,2,3,1)
		result = [a.call("sum", numbers, m) for a in ags]
		should_be = [7] * len(ags)
		for a in ags:
			a.stop(m)
		self.assertEqual(result, should_be)
		m.destroy()

	def test_pcall(self):
		ags = [AgentTracer("agent#%s" % x, multiprocessing.Process,
			latency=AgentTracer.Latency.EXTRA_LOW)
			   for x in xrange(0, 16)]
		m = MailBox("agency mailbox")
		numbers = (1,2,3,1)
		result = [a.call("sum", numbers, m) for a in ags]
		should_be = [7] * len(ags)
		for a in ags:
			a.stop(m)
		self.assertEqual(result, should_be)
		m.destroy()

class AgencyTest(unittest.TestCase):

	def test_init(self):
		mb = MailBox(MAILBOX_ADDRESS_1)
		a = Agency()
		self.assertEquals(type(a), Agency)
		a.stop(mb)

	def test_address(self):
		mb = MailBox(MAILBOX_ADDRESS_1)
		a = Agency()
		addresses = [a.alloc_address(mb) for _ in xrange(0, 8)]
		exists = [a.addr_exists(addr,mb) for addr in addresses]
		for addr in addresses:
			a.free_address(addr,mb)
		doesnt_exists = [a.addr_exists(addr,mb) for addr in addresses]
		a.stop(mb)
		self.assertTrue(all(exists))
		self.assertFalse(any(doesnt_exists))


from collector.test import *

if __name__ == "__main__":
	setup_environment()
	unittest.main()