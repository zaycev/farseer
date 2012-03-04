# -*- coding: utf-8 -*-

from sqlalchemy import Column, func
from sqlalchemy.types import Integer, String
from options import DATABASE_CONFIG
from analyzer.model import DbBase, TaggedTerm, DocumentStat, DocTerm
from analyzer.nlp import NlpUtil
from analyzer.acessdb import make_environment
from multiprocessing import Pool

import analyzer.nlp as nlp
import logging
import time, datetime
import gc

DEFAULT_TEXT_FIELDS = (
	(0, "title"),
	(1, "short_text"),
	(2, "full_text"),
)


def index(input_tab="set_corpora",
			text_fields=DEFAULT_TEXT_FIELDS,
			workers=4,
			buff_size=256):
	"""
	"""

	# step 1
	# Creating an ORM environment: establishing database
	# connection, classes for input and output table
	# mapping.
	logging.debug("setup ORM environment")
	db_engine, db_session = make_environment(DATABASE_CONFIG["repository"])
	doc_class_fields = {field_name[1]: Column(String) for field_name in text_fields}
	doc_class_fields["id"] = Column(Integer, primary_key=True)
	doc_class_fields["__tablename__"] = input_tab
	TextDoc = type("TextDoc", (DbBase,), doc_class_fields)
	DbBase.metadata.create_all(db_engine)


	# step 2
	logging.debug("loading term cache")
	term_cache = dict()
	for term in db_session.query(TaggedTerm).order_by("nertag").yield_per(4096):
		key = make_tagged_term_key(term)
		term_cache[key] = term.id
	logging.debug("loaded {0} terms".format(len(term_cache)))

	# step 3
	# Retrieving corpora (input data) size.
	logging.debug("retrieving corpora ({0}) set size".format(input_tab))
	corpora_sz = db_session.query(func.count("id")).select_from(TextDoc).scalar()
	logging.debug("corpora size is {0}".format(corpora_sz))


#	# step 4
#	# Setting up processing environment.
	logging.debug("setup processing environment")
	pool = Pool(workers, initializer=lambda: init_worker(term_cache) )
	text_buff = []
	docs_handled = 0
	star_time = datetime.datetime.now()

	# step 5
	# Retrieve documents from corpora and process them.
	logging.debug("start processing data")
	for doc in db_session.query(TextDoc).order_by("id").yield_per(buff_size * workers):
		docs_handled += 1
		text_set = (doc.id, [
			(text_field[0], getattr(doc, text_field[1]),)
			for text_field in text_fields])
		text_buff.append(text_set)
		if (len(text_buff) >= buff_size) or (corpora_sz == docs_handled):
			indexed_docs = pool.map(map_text_to_docterms, text_buff)
			save_indexed_docs(indexed_docs, db_session)
			db_session.commit()
			db_session.flush()
			text_buff = []
			gc.collect()
			elapsed = (datetime.datetime.now() - star_time).seconds
			logging.debug("\t :: {0:2.2f}%\t {1} / {2}\t worktime {3} sec\t ave speed {4:0.2f} d / sec".format(
				float(docs_handled * 100) / float(corpora_sz),
				corpora_sz,
				docs_handled,
				elapsed,
				float(docs_handled) / float(elapsed)
			))


	logging.debug("done!\n")

def init_worker(term_cache):
	nlp.util = NlpUtil()
	nlp.term_cache = term_cache

def map_text_to_docterms(text_set):
	docterms = []
	# docterms : (<DocumentStat>, [<DocTerm>])
	# docterm: [(term_key, term_count)]
	# docstat: (<id>, <wcount>, <scount>, <smed>, <savg>)
	doc_id, texts = text_set
	wcount = 0
	scount = 0
	snt_lenghts = []
	for field_id, text in texts:
		field_term_counter = dict()
		snts = nlp.util.snt_tokenizer.tokenize(text)
		csnts = nlp.util.snt_corrector.correct(snts)
		tokens = []
		for s in csnts:
			s_tokens = nlp.util.wrd_tokenizer.tokenize(s)
			tokens.extend(s_tokens)
			snt_lenghts.append(len(s_tokens))
		scount += len(csnts)
		wcount += len(tokens)
		ttokens = nlp.util.pos_tag(tokens)
		ttoken_tree = nlp.util.ner_tag(ttokens)
		for elem in ttoken_tree:
			if type(elem) is tuple:
				token, tag = elem[0].lower(), elem[1].lower()
				nertag = None
			else:
				nertag = elem.node.lower()
				tokens = elem.leaves()
				tokens.sort(key=lambda e: e[0])
				tokens = [(e[0].lower(), e[1].lower(),) for e in tokens]
				token, tag = tokens[0]
				for tk, tg in tokens[1:len(tokens)]:
					token += "+" + tk
					tag += "+" + tg
			token_key = make_token_key(token, tag, nertag)

			tid = nlp.term_cache.get(token_key, -1)
			if tid != -1:
				if tid in field_term_counter:
					field_term_counter[tid] += 1
				else:
					field_term_counter[tid] = 1

		docterms.append((field_id, field_term_counter))

	snt_lenghts.sort()
	savg = float(sum(snt_lenghts) / float(len(snt_lenghts)))
	smed = snt_lenghts[len(snt_lenghts) / 2]
	gc.collect()
	doc_stat = (doc_id, wcount, scount, smed, savg)
	#print "\n\n\n", doc_stat, docterms, "\n\n\n"
	return doc_stat, docterms

def save_indexed_docs(indexed_docs, db_session):
	for doc_stat, term_counters in indexed_docs:
		doc = DocumentStat(*doc_stat)
		db_session.add(doc)
		for field_id, term_counter in term_counters:
			for tid in term_counter.iterkeys():
				dt = DocTerm(tid, doc_stat[0], field_id, term_counter[tid])
				db_session.add(dt)
		db_session.commit()
		db_session.flush()


def make_tagged_term_key(tagged_term):
	nertag = tagged_term.nertag
	tag = tagged_term.tag
	term = tagged_term.term
	return make_token_key(term, tag, nertag)

def make_token_key(token, tag, nertag):
	return u"{0}-{1}-{2}".format(nertag, tag, token)