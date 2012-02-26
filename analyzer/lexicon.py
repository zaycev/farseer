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

DEFAULT_TEXT_FIELDS = ("title", "short_text", "full_text",)


def lexicon(input_table_name="set_input",
			lexicon_table_name="set_lexicon",
			text_fields=DEFAULT_TEXT_FIELDS,
			csv_output="/tmp/set_lexicon.csv",
			verbose=True):
	"""
	This function takes documents from input table,
	extracts terms from specified in <text_fields>
	fields and saves terms with calculated frequencies
	in output table. If csv_output is defined terms will
	be saved to the csv file instead of lexicon table.
	"""


	# step 1
	# Establishing database connection and creating
	# an orm environment - classes fpr input and output
	# table mapping.
	logging.debug("establish database connection")
	db_url = URL(
		DATABASE_CONFIG["repository"]["driver"],
		username=DATABASE_CONFIG["repository"]["user"],
		password=DATABASE_CONFIG["repository"]["password"],
		host=DATABASE_CONFIG["repository"]["host"],
		port=DATABASE_CONFIG["repository"]["port"],
		database=DATABASE_CONFIG["repository"]["database"],)
	db_base = declarative_base()
	db_engine = create_engine(db_url)
	db_session = sessionmaker(bind=db_engine, autoflush=False)()
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
	corpus_class_fields = {field_name: Column(String) for field_name in text_fields}
	corpus_class_fields["id"] = Column(Integer, primary_key=True)
	corpus_class_fields["__tablename__"] = input_table_name
	CorpusDoc = type("CorpusDoc", (db_base,), corpus_class_fields)


	# step 2
	# Creating or truncating the target (lexicon) table.
	logging.debug("create or truncate target (lexicon) table")
	db_base.metadata.create_all(db_engine)
	db_session.query(LexiconTerm).delete()


	# step 3
	# Retrieving corpus (input data) size.
	logging.debug("retrieving corpus (input) size")
	corpus_sz = db_session.query(func.count("id")).select_from(CorpusDoc).scalar()
	logging.debug("corpus size is {0}".format(corpus_sz))


	# step 4
	# Retrieve documents from corpus and
	# calculating different kinds term frequencies.
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
		# Getting texts from document.
		texts = [getattr(doc, text_field) for text_field in text_fields]
		# Use this set to account terms which were already
		# occurred in the given document to not count them
		# twice.
		doc_occurrences = set()
		# Extracting terms from texts.
		for text in texts:
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
	if verbose:
		sys.stdout.write("\n")
		sys.stdout.flush()


	# step 4
	# Calculating relative frequencies and saving terms.
	logging.debug("recounting terms")
	i = 1
	corpus_sz_f = float(corpus_sz)
	logging.debug("lexicon has {0} terms".format(len(terms_dict)))
	lex_terms = []
	for term in terms_dict.keys():
		lex_term = terms_dict[term]
		lex_term.rfreq = float(lex_term.dfreq) / corpus_sz_f
		lex_term.id = i
		i += 1
		lex_terms.append(lex_term)
	logging.debug("saving terms")
	if csv_output:
		csv_file = open(csv_output, "w")
		cols = "id,term,tfreq,dfreq,rfreq\n"
		pattern = u"{0},\"{1}\",{2},{3},{4:0.16f}\n"
		csv_file.write(cols)
		for l_term in lex_terms:
			csv_file.write(
				pattern.format(
					l_term.id,
					l_term.term,
					l_term.tfreq,
					l_term.dfreq,
					l_term.rfreq
				).encode("UTF-8")
			)
		csv_file.close()
	else:
		db_session.add_all(lex_terms)
		db_session.commit()
		db_session.flush()