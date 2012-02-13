# -*- coding: utf-8 -*-
# Implementation of abstractions allowing
# to work with Redis connections as with
# python Queue from multiprocssing

import time
import redis
from options import DATABASE_CONFIG
from collector.core.task import deserialize

class Singleton(type):

	def __init__(cls, name, bases, dict):
		super(Singleton, cls).__init__(name, bases, dict)
		cls.instance = None

	def __call__(cls,*args,**kw):
		if cls.instance is None:
			cls.instance = super(Singleton, cls).__call__(*args, **kw)
		return cls.instance


class RedisConnectionKeeper(object):
	__metaclass__ = Singleton

	def __init__(self):
		self.queues = 0
		self.timeout = DATABASE_CONFIG["redis"].get("timeout", 1)
		self.__conn = redis.StrictRedis(
			db=DATABASE_CONFIG["redis"].get("db", 0),
			port=DATABASE_CONFIG["redis"].get("port", 6379),
			host=DATABASE_CONFIG["redis"].get("host", "127.0.0.1"),
		)
		if DATABASE_CONFIG["redis"].get("flushdb", False):
			self.__conn.flushdb()

	@property
	def conn(self):
		return self.__conn

	def new_queue_name(self):
		self.queues += 1
		return str(self.queues)


class RQueue:
	keeper=RedisConnectionKeeper()

	def __init__(self, max_size=512):
		self.max_size = max_size
		self.name = self.keeper.new_queue_name()
		print self.name

	def put(self, task):
		while self.keeper.conn.llen(self.name) > 512:
			time.sleep(self.keeper.timeout)
		self.keeper.conn.lpush(self.name, task.serialize())

	def get(self):
		while True:
			if self.keeper.conn.llen(self.name) > 0:
				task_blob = self.keeper.conn.rpop(self.name)
				if task_blob:
					task = deserialize(task_blob)
					return task
				else:
					time.sleep(self.keeper.timeout)
			else:
				time.sleep(self.keeper.timeout)