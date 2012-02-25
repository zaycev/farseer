# -*- coding: utf-8 -*-

# This module contains code which allows to extract lexicon from corpus
# of texts. Corpus is just a set of text documents. Lexicon is set of
# terms extracted from the given corpus with counted term frequencies
# and document frequencies.

from options import DATABASE_CONFIG
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, String, Float
from sqlalchemy.engine.url import URL
from sqlalchemy import Column, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from analyzer.nlp import tokenize


import logging
import sys

DEFAULT_WEIGHT_SCHEMA = (

#	input table			tf-idf
# 	column nane			weight

	("title",			0.5),
	("short_text",		0.4),
	("full_text",		0.1),

)  


def lexicon(input_table_name="set_input",
			lexicon_table_name="set_lexicon",
			weight_schema=DEFAULT_WEIGHT_SCHEMA,
			verbose=True):
	'''
		This function takes documents from input table,
		extracts terms from specified in weight_schema
		fields and saves terms with calculated frequencies
		in output table.
	'''

	# step 1
	# establish database connection
	logging.debug("establish database connection")
	db_url = URL(
		DATABASE_CONFIG["repository"]["driver"],
		username=DATABASE_CONFIG["repository"]["user"],
		password=DATABASE_CONFIG["repository"]["password"],
		host=DATABASE_CONFIG["repository"]["host"],
		port=DATABASE_CONFIG["repository"]["port"],
		database=DATABASE_CONFIG["repository"]["database"],
	)
	db_base = Base = declarative_base()
	db_engine = create_engine(db_url)
	db_session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)()
	class LexiconTerm(db_base):
		__tablename__ = lexicon_table_name
		id = Column(Integer, primary_key=True)		# lexicon term id
		term = Column(String)						# term string
		tfreq = Column(Integer)						# total terms frequency
		dfreq = Column(Integer)						# term document frequency
		rfreq = Column(Float)						# relative document frequency
		def __init__(self, term):
			self.term = term
			self.tfreq = 0
			self.dfreq = 0
			self.rfreq = 0.0
		def __repr__(self):
			return "<LexiconTerm('{0}')>".format(self.term)
	corpus_class_fields = {param[0]: Column(String) for param in weight_schema}
	corpus_class_fields["id"] = Column(Integer, primary_key=True)
	corpus_class_fields["__tablename__"] = input_table_name
	CorpusDoc = type("CorpusDoc", (db_base,), corpus_class_fields)

	# step 2
	# create or truncate target (lexicon) table
	logging.debug("create or truncate target (lexicon) table")
	db_base.metadata.create_all(db_engine)
	db_session.query(LexiconTerm).delete()

	# step 3
	# retrieving corpus (input) size
	logging.debug("retrieving corpus (input) size")
	corpus_sz = db_session.query(func.count("id")).select_from(CorpusDoc).scalar()
	logging.debug("corpus size is {0}".format(corpus_sz))


	# step 4
	# retrieve documents from corpus(input table)
	# and calculate TF-IDF using weight schema
	logging.debug("start retrieve documents from the corpus")
	if verbose:
		progress_bar_sz = 80
		loop_step_size = corpus_sz / progress_bar_sz
		loop_steps = 0
		for i in xrange(progress_bar_sz):
			sys.stdout.write("–")
		sys.stdout.write("\n")
		sys.stdout.flush()
	terms_dict = dict()
	for doc in db_session.query(CorpusDoc).order_by("time").yield_per(128):

		doc_occurrences = set()

		# getting texts from doc and assigning appropriate weights
		texts = [(param[1], getattr(doc, param[0])) for param in weight_schema]

		# tokenizing texts
		for weight, text in texts:
			terms = tokenize(text)
			for term in terms:
				if term not in terms_dict:
					lex_term = LexiconTerm(term)
					terms_dict[term] = lex_term
				else:
					lex_term = terms_dict[term]
				lex_term.tfreq += 1
				if term not in doc_occurrences:
					doc_occurrences.add(term)
					lex_term.dfreq += 1

		if verbose:
			loop_steps += 1
			if loop_steps % loop_step_size == 0:
				sys.stdout.write("#")
				sys.stdout.flush()

	# step 4
	# saving terms
	logging.debug("recounting terms")
	i = 1
	corpus_sz_f = float(corpus_sz)
	lex_terms = []
	for term in terms_dict.keys():
		lex_term = terms_dict[term]
		lex_term.rfreq = float(lex_term.dfreq) / corpus_sz_f
		lex_term.id = i
		i += 1
		lex_terms.append(lex_term)
	logging.debug("saving terms")
	db_session.add_all(lex_terms)
	db_session.commit()
	db_session.flush()