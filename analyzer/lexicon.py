# -*- coding: utf-8 -*-

# This module contains code which allows to extract lexicon from corpora
# of texts. Corpora is a set of text documents. Lexicon is set of
# terms extracted from the given corpora with counted term frequencies
# and document frequencies. Additionally term POS tag can be also extracted.

from sqlalchemy import Column, func
from sqlalchemy.types import Integer, String
from options import DATABASE_CONFIG
from analyzer.term import DbBase, TaggedTerm
from analyzer.nlp import NlpUtil
from analyzer.acessdb import make_environment
from multiprocessing import Pool

import analyzer.nlp as nlp
import logging
import time, datetime
import gc

DEFAULT_TEXT_FIELDS = ("title", "short_text", "full_text",)


def lexicon(input_tab="set_corpora",
			output_tab=None,
			text_fields=DEFAULT_TEXT_FIELDS,
			csv_output=None,
			workers=4,
			buff_size=64,
			recount_buffer=16384):
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
	term_class = TaggedTerm
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
	db_session.query(LexiconTerm).delete(synchronize_session=False)


	# step 3
	# Retrieving corpora (input data) size.
	logging.debug("retrieving corpora ({0}) set size".format(input_tab))
	corpora_sz = db_session.query(func.count("id")).select_from(TextDoc).scalar()
	logging.debug("corpora size is {0}".format(corpora_sz))


	# step 4
	# Setting up processing environment.
	logging.debug("setup processing environment")
	pool = Pool(workers, initializer=init_worker)
	text_buff = []
	docs_handled = 0
	star_time = datetime.datetime.now()
	terms_dict = dict()

	# step 5
	# Retrieve documents from corpora and process them.
	logging.debug("start processing data")
	corpora_sz = 1024
	for doc in db_session.query(TextDoc).order_by("id").yield_per(buff_size * workers)[0:1024]:
		docs_handled += 1
		text_set = [getattr(doc, text_field) for text_field in text_fields]
		text_buff.append(text_set)
		if len(text_buff) > buff_size:
			term_sets = pool.map(count_terms, text_buff)
			for term_set in term_sets:
				for k in term_set.keys():
					token, tag, nertag, freq = term_set[k]
					term = terms_dict.get(k)
					if term:
						_, _, _, old_freq, old_dferq = term
						term_set[k] = (token, tag, nertag, old_freq + freq, old_dferq + 1)
					else:
						term = (token, tag, nertag, freq, 1)
						terms_dict[k] = term
			text_buff = []
			gc.collect()
			elapsed = (datetime.datetime.now() - star_time).seconds
			print "\t :: {0:2.2f}%\t {1} / {2}\t worktime {3} sec\t ave speed {4:0.2f} d / sec".format(
				float(docs_handled * 100) / float(corpora_sz),
				corpora_sz,
				docs_handled,
				elapsed,
				float(docs_handled) / float(elapsed)
			)


	if len(text_buff) > buff_size:
		term_sets = pool.map(count_terms, text_buff)
		for term_set in term_sets:
			for k in term_set.keys():
				token, tag, nertag, freq = term_set[k]
				term = terms_dict.get(k)
				if term:
					_, _, _, old_freq, old_dferq = term
					term_set[k] = (token, tag, nertag, old_freq + freq, old_dferq + 1)
				else:
					term = (token, tag, nertag, freq, 1)
					terms_dict[k] = term
	text_buff = []
	pool.close()
	gc.collect()

	elapsed = (datetime.datetime.now() - star_time).seconds
	print "\t :: {0:2.2f}%\t {1} / {2}\t worktime {3} sec\t ave speed {4:0.2f} d/sec".format(
		float(docs_handled * 100) / float(corpora_sz),
		corpora_sz,
		docs_handled,
		elapsed,
		float(docs_handled) / float(elapsed)
	)

	# step 4
	# Calculating relative frequencies and saving terms.
	logging.debug("recounting terms")
	corpora_sz_f = float(corpora_sz)
	terms_count = len(terms_dict)
	logging.debug("lexicon has {0} terms".format(terms_count))
	logging.debug("saving terms")
	terms_saved = 0
	star_time = datetime.datetime.now()
	time.sleep(1)
	for term_tuple in terms_dict.itervalues():
		term, tag, nertag, tfreq, dferq = term_tuple
		t = TaggedTerm(term, tag, nertag)
		t.tfreq = tfreq
		t.dfreq = dferq
		t.rfreq = float(dferq) / corpora_sz_f
		db_session.add(t)
		terms_saved += 1
		if not terms_saved % recount_buffer:
			db_session.commit()
			db_session.flush()
			elapsed = (datetime.datetime.now() - star_time).seconds
			print "\t :: {0:2.2f}%\t {1} / {2}\t savetime {3} sec\t ave speed {4:0.2f} t/sec".format(
				float(terms_saved * 100) / float(terms_count),
				terms_count,
				terms_saved,
				elapsed,
				float(terms_saved) / float(elapsed)
			)
	db_session.commit()
	db_session.flush()
	elapsed = (datetime.datetime.now() - star_time).seconds
	print "\t :: {0:2.2f}%\t {1} / {2}\t savetime {3} sec\t ave speed {4:0.2f} t/sec".format(
		float(terms_saved * 100) / float(terms_count),
		terms_count,
		terms_saved,
		elapsed,
		float(terms_saved) / float(elapsed)
	)
	logging.debug("done!\n")





#	lex_terms = []
#	for term in terms_dict.keys():
#		lex_term = terms_dict[term]
#		lex_term.rfreq = float(lex_term.dfreq) / corpora_sz_f
#		lex_term.id = i
#		i += 1
#		lex_terms.append(lex_term)
#	logging.debug("saving terms")
#	if csv_output:
#		csv_file = open(csv_output, "w")
#		cols = "id,term,tag,nertag,tfreq,dfreq,rfreq\n"
#		pattern = u"{0},\"{1}\",\"{2}\",\"{3}\",{5},{6},{7:0.16f}\n"
#		csv_file.write(cols)
#		for lex_term in lex_terms:
#			csv_file.write(
#				pattern.format(
#					lex_term.id,
#					lex_term.term.replace("\"","''"),
#					lex_term.tag.replace("\"","''"),
#					lex_term.nertag.replace("\"","''"),
#					lex_term.tfreq,
#					lex_term.dfreq,
#					lex_term.rfreq
#				).encode("UTF-8")
#			)
#		csv_file.close()
#	else:
#		db_session.add_all(lex_terms)
#		db_session.commit()
#		db_session.flush()


def init_worker():
	nlp.util = NlpUtil()

def count_terms(text_set):
	counter = dict()
	# counter : key -> (<token>, <tag>, <ner_tag>, <freq>)
	for text in text_set:
		tokens = nlp.util.tokenize(text)
		ttokens = nlp.util.pos_tag(tokens)
		ttoken_tree = nlp.util.ner_tag(ttokens)
		for elem in ttoken_tree:
			if elem.__class__.__name__ == "tuple":
				# handle non NER chunk
				token, tag = elem
				token_key = token+tag
				nertag = None
			else:
				# handle NER chunk, considering tree has height equal to 1
				nertag = elem.node
				tokens = elem.leaves()
				token, tag = tokens[0]
				for tk, tg in tokens[1:len(tokens)]:
					token += "+" + tk
					tag += "+" + tg
				token_key = "NER" + token + tag
			if token_key not in counter:
				counter[token_key] = (token, tag, nertag, 1)
			else:
				prev_count = counter[token_key][3]
				counter[token_key] = (token, tag, nertag, prev_count + 1)
	gc.collect()
	return counter