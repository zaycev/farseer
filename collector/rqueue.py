# -*- coding: utf-8 -*-
# Implementation of abstractions allowing
# to work with Redis connections as with
# python Queue from multiprocssing

import time
import redis
import random
import logging
from options import DATABASE_CONFIG
from collector.task import deserialize

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


class QConnPool(object):
	__metaclass__ = Singleton

	def __init__(self):
		self.timeout = DATABASE_CONFIG["redis"].get("timeout", 1)
		self.__pool = None
		self.__sys_conn = None

	def initialize(self):
		self.__pool = redis.ConnectionPool(
			db=DATABASE_CONFIG["redis"].get("db", 0),
			port=DATABASE_CONFIG["redis"].get("port", 6379),
			host=DATABASE_CONFIG["redis"].get("host", "127.0.0.1"),
		)
		self.__sys_conn = redis.StrictRedis(connection_pool=self.__pool)


	def flush_db(self):
		logging.debug("flushing redis db")
		self.__sys_conn.flushdb()
		logging.debug("now redis db size is {0}".format(self.__sys_conn.dbsize()))

	def allocate_queue(self, max_size=512):
		name = gen_key()
		return lambda: RQueue(self, name, max_size)

	def allocate_connection(self,name):
		while not self.__pool:
			time.sleep(self.timeout)
		return redis.Redis(connection_pool=self.__pool)


class RQueue:
	timeout = DATABASE_CONFIG["redis"].get("timeout", 1)

	def __init__(self, pool, name, size):
		self.name = name
		self.size = size
		self.conn = pool.allocate_connection(self.name)

	def __len__(self):
		return self.conn.llen(self.name)

	def put(self, task):
		self.conn.lpush(self.name, task.serialize())

	def get(self):
		task_blob = self.conn.rpop(self.name)
		if task_blob:
			try:
				task = deserialize(task_blob)
				return task
			except:
				logging.debug("task deserialization error, task={0}, name={1}".format(task_blob, self.name))