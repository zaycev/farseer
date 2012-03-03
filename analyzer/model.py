# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.types import Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

DbBase = declarative_base()

class TaggedTerm(DbBase):
	__tablename__ = "set_term"					# default terms table
	id = Column(Integer, primary_key=True)		# lexicon term id
	term = Column(String)						# term string
	tag = Column(String)						# part of speech tag
	nertag = Column(String)						# NER tag
	tfreq = Column(Integer)						# total terms frequency
	dfreq = Column(Integer)						# term document frequency
	rfreq = Column(Float)						# relative document frequency

	def __init__(self, term, tag, nertag):
		self.term = term
		self.nertag = nertag
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