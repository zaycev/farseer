# -*- coding: utf-8 -*-

# This module contains code which allows to extract lexicon from corpora
# of texts. Corpora is a set of text documents. Lexicon is set of
# terms extracted from the given corpora with counted term frequencies
# and document frequencies. Additionally term POS tag can be also extracted.

from sqlalchemy import Column, func
from sqlalchemy.types import Integer, String
from options import DATABASE_CONFIG
from analyzer.term import DbBase, UntaggedTerm, TaggedTerm
from analyzer.nlp import make_tokenizer, make_tagger, assign_tags
from analyzer.acessdb import make_environment
from multiprocessing import Pool

import analyzer.nlp as nlp
import logging
import sys

DEFAULT_TEXT_FIELDS = ("title", "short_text", "full_text",)


def lexicon(input_tab="set_corpora",
			output_tab=None,
			text_fields=DEFAULT_TEXT_FIELDS,
			csv_output=None,
			verbose=True,
			pos_tagging=True,
			workers=7,
			buff_size=1536):
	"""
	This function takes documents from input table,
	extracts terms from specified in <text_fields>
	fields and saves terms with calculated frequencies
	in output table. If <csv_output> is defined terms will
	be saved to the csv file instead of output table.
	"""


	# step 1
	# Creating an ORM environment: establishing database
	# connection, classes for input and output table
	# mapping.
	logging.debug("setup ORM environment")
	term_class = TaggedTerm if pos_tagging else UntaggedTerm
	class LexiconTerm(term_class, DbBase):
		__tablename__ = output_tab if output_tab else term_class.__tablename__
	db_engine, db_session = make_environment(DATABASE_CONFIG["repository"])
	doc_class_fields = {field_name: Column(String) for field_name in text_fields}
	doc_class_fields["id"] = Column(Integer, primary_key=True)
	doc_class_fields["__tablename__"] = input_tab
	TextDoc = type("TextDoc", (DbBase,), doc_class_fields)


	# step 2
	# Creating or truncating the target (output) table.
	logging.debug("create or truncate target ({0}) table".format(output_tab))
	DbBase.metadata.create_all(db_engine)
	db_session.query(LexiconTerm).delete()


	# step 3
	# Retrieving corpora (input data) size.
	logging.debug("retrieving corpora ({0}) set size".format(input_tab))
	corpora_sz = db_session.query(func.count("id")).select_from(TextDoc).scalar()
	logging.debug("corpora size is {0}".format(corpora_sz))


	# step 4
	# Setting up processing environment.
	logging.debug("setup processing environment")
	pool = Pool(workers)
	text_buff = []
	term_lists_handled = 0
	terms_dict = dict()
	if verbose:
		progress_bar_sz = 100
		loop_step_size = corpora_sz / progress_bar_sz
		loop_steps = 0


	# step 5
	# Retrieve documents from corpora and process them.
	logging.debug("start retrieve data")
	for doc in db_session.query(TextDoc).order_by("id").yield_per(512):
		texts = [getattr(doc, text_field) for text_field in text_fields]
		for text in texts:
			text_buff.append(text)
		if len(text_buff) > buff_size:
			term_lists = pool.map(tokenize, text_buff)
			if pos_tagging:
				term_lists = pool.map(pos_tag, term_lists)
			for term_list in term_lists:
				term_lists_handled += 1
				doc_occurrences = set()
				for elem in term_list:
					if pos_tagging:
						term, tag = elem
					else:
						term = elem
						tag = None
					term_key = term_class.make_key(term, tag)
					if term_key not in terms_dict:
						lex_term = LexiconTerm(term, tag)
						terms_dict[term_key] = lex_term
					else:
						lex_term = terms_dict[term_key]
					lex_term.tfreq += 1
					if term_key not in doc_occurrences:
						doc_occurrences.add(term_key)
						lex_term.dfreq += 1
			text_buff = []
		if verbose:
			loop_steps += 1
			if loop_steps % loop_step_size == 0:
				sys.stdout.write("#")
				sys.stdout.flush()

	if verbose:
		sys.stdout.write("\n")
		sys.stdout.flush()


	if len(text_buff) > 0:
		term_lists = pool.map(tokenize, text_buff)
		if pos_tagging:
			term_lists = pool.map(pos_tag, term_lists)
		for term_list in term_lists:
			term_lists_handled += 1
			doc_occurrences = set()
			for elem in term_list:
				if pos_tagging:
					term, tag = elem
				else:
					term = elem
					tag = None
				term_key = term_class.make_key(term, tag)
				if term_key not in terms_dict:
					lex_term = LexiconTerm(term, tag)
					terms_dict[term_key] = lex_term
				else:
					lex_term = terms_dict[term_key]
				lex_term.tfreq += 1
				if term_key not in doc_occurrences:
					doc_occurrences.add(term_key)
					lex_term.dfreq += 1
	# text_buff = []
	# term_lists = []

	# step 4
	# Calculating relative frequencies and saving terms.
	logging.debug("recounting terms")
	i = 1
	corpora_sz_f = float(corpora_sz)
	logging.debug("lexicon has {0} terms".format(len(terms_dict)))
	lex_terms = []
	for term in terms_dict.keys():
		lex_term = terms_dict[term]
		lex_term.rfreq = float(lex_term.dfreq) / corpora_sz_f
		lex_term.id = i
		i += 1
		lex_terms.append(lex_term)
	logging.debug("saving terms")
	if csv_output:
		csv_file = open(csv_output, "w")
		cols = "id,term,tag,tfreq,dfreq,rfreq\n"
		pattern = u"{0},\"{1}\",\"{2}\",{3},{4},{5:0.16f}\n"
		csv_file.write(cols)
		for lex_term in lex_terms:
			csv_file.write(
				pattern.format(
					lex_term.id,
					lex_term.term.replace("\"","''"),
					lex_term.tag.replace("\"","''"),
					lex_term.tfreq,
					lex_term.dfreq,
					lex_term.rfreq
				).encode("UTF-8")
			)
		csv_file.close()
	else:
		db_session.add_all(lex_terms)
		db_session.commit()
		db_session.flush()


def init_worker(pos_tagging):
	if pos_tagging:
		nlp.Tagger = make_tagger()
	nlp.Tokenizer = make_tokenizer()


def count_terms(text):
	tokens = nlp.Tokenizer.tokenize(text)



def tokenize(text):
	tokenizer = make_tokenizer()
	return tokenizer.tokenize(text)


def pos_tag(token_list):
	return assign_tags(token_list)