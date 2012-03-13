# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.types import Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from analyzer.acessdb import make_environment
from options import DATABASE_CONFIG
import math

DbBase = declarative_base()

class Document(DbBase):
	__tablename__ = "set_corpora"
	id = Column(Integer, primary_key=True)
	uri = Column(String)
	title = Column(String)
	short_text = Column(String)
	full_text = Column(String)
	views = Column(Integer)
	com  = Column(Integer)
	fb_com = Column(Integer)
	fb_shr = Column(Integer)
	tw = Column(Integer)
	su = Column(Integer)
	dg = Column(Integer)
	li = Column(Integer)
	score = Column(Float)
	time = Column(DateTime)

	@property
	def lscore(self):
#		print
		return "{0:2.3f}".format(math.log(self.score))





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

	@property
	def pretty_term(self):
		return self.term.replace("+", " ")

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

db_engine, db_session = make_environment(DATABASE_CONFIG["repository"])
DbBase.metadata.create_all(db_engine)