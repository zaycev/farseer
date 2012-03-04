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


class DocumentStat(DbBase):
	__tablename__ = "set_docstat"				#
	id = Column(Integer, primary_key=True)		#
	wcount = Column(Integer)					#
	scount = Column(Integer)					#
	smed = Column(Integer)						#
	savg = Column(Float)						#

	def __init__(self, id, wcount, scount, smed, savg):
		self.id = id
		self.wcount = wcount
		self.scount = scount
		self.smed = smed
		self.savg = savg


	def __repr__(self):
		return "<DocumentStat('{0}', '{1}')>".format(self.id)

class DocTerm(DbBase):
	__tablename__ = "set_docterm"				#
	tid = Column(Integer, primary_key=True)		#
	did = Column(Integer, primary_key=True)		#
	fid = Column(Integer, primary_key=True)						#
	count = Column(Integer)						#

	def __init__(self, tid, did, fid, count):
		self.tid = tid
		self.did = did
		self.fid = fid
		self.count = count

	def __repr__(self):
		return "<DocTerm('{0}', '{1}')>".format(self.did, self.tid)