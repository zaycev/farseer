# -*- coding: utf-8 -*-
# Implementation of abstractions allowing
# to work with Redis connections as with
# python Queue from multiprocssing

import time
import redis
import random
import logging
import traceback
from options import DATABASE_CONFIG
from collector.core.task import deserialize

ALPHABET = "abcdefghijklmnopqrstuvwxyz" \
		   "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
		   "0123456789~!@#$%^&*()_+<>?"
KEY_LEN = 8

def gen_key():
	name = ""
	for x in random.sample(ALPHABET, KEY_LEN):
		name += x
	return name

class Singleton(type):

	def __init__(cls, name, bases, dict):
		super(Singleton, cls).__init__(name, bases, dict)
		cls.instance = None

	def __call__(cls,*args,**kw):
		if cls.instance is None:
			cls.instance = super(Singleton, cls).__call__(*args, **kw)
		return cls.instance


class CPoolSingleton(object):
	__metaclass__ = Singleton

	def __init__(self):
		self.queues = 0
		self.timeout = DATABASE_CONFIG["redis"].get("timeout", 1)
		self.__pool = redis.ConnectionPool(
			db=DATABASE_CONFIG["redis"].get("db", 0),
			port=DATABASE_CONFIG["redis"].get("port", 6379),
			host=DATABASE_CONFIG["redis"].get("host", "127.0.0.1"),
		)
		self.__sys_conn = redis.StrictRedis(connection_pool=self.__pool)

	def new_conn(self):
		return redis.Redis(connection_pool=self.__pool)

	def new_queue_name(self):
		return gen_key()

	@property
	def sys_conn(self):
		return self.__sys_conn

keeper = CPoolSingleton()
def flush_db():
	logging.debug("flushing redis db")
	keeper.sys_conn.flushdb()
	logging.debug("now redis db size is {0}".format(keeper.sys_conn.dbsize()))

class RQueue:
	timeout = keeper.timeout

	def __init__(self, name, max_size=512):
		self.max_size = max_size
		self.name = name#keeper.new_queue_name()
		self.conn = keeper.new_conn()

	def put(self, task):
#		while self.conn.llen(self.name) > self.max_size:
#			time.sleep(self.timeout)
		self.conn.lpush(self.name, task.serialize())

	def get(self):
		while True:
			task_blob = self.conn.rpop(self.name)
			if task_blob:
				try:
					task = deserialize(task_blob)
					return task
				except:
					logging.debug("task deserialize erroa, task={0}, name={1}".format(task_blob, self.name))
			else:
				time.sleep(self.timeout)