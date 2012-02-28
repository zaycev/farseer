# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.types import Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

DbBase = declarative_base()

class UntaggedTerm(DbBase):
	__tablename__ = "set_uterm"					# default terms table
	id = Column(Integer, primary_key=True)		# lexicon term id
	term = Column(String)						# term string
	tfreq = Column(Integer)						# total terms frequency
	dfreq = Column(Integer)						# term document frequency
	rfreq = Column(Float)						# relative document frequency

	def __init__(self, term, *args):
		self.term = term
		self.tfreq = 0
		self.dfreq = 0
		self.rfreq = 0.0

	def key(self):
		return self.term

	@staticmethod
	def make_key(term, *args):
		return term

	def __repr__(self):
		return "<UntaggedTerm('{0}')>".format(self.term)

class TaggedTerm(DbBase):
	__tablename__ = "set_tterm"					# default terms table
	id = Column(Integer, primary_key=True)		# lexicon term id
	term = Column(String)						# term string
	tfreq = Column(Integer)						# total terms frequency
	dfreq = Column(Integer)						# term document frequency
	rfreq = Column(Float)						# relative document frequency
	tag = Column(String)						# part of speech tag

	def __init__(self, term, tag, *arg):
		self.term = term
		self.tag = tag
		self.tfreq = 0
		self.dfreq = 0
		self.rfreq = 0.0

	def key(self):
		return self.term + self.tag

	@staticmethod
	def make_key(term, key, *args):
		return term + key

	def __repr__(self):
		return "<TaggedTerm('{0}', '{1}')>".format(self.term, self.tag)