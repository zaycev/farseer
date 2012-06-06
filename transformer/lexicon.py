# -*- coding: utf-8 -*-

from multiprocessing import Pool
from transformer.nlp import count_terms

import collector.models as cm
import transformer.models as am
import django.db
import datetime
import logging
import time
import gc


def make_lexicon(input_dataset, output_dataset=None, workers=4, buff_size=256,
				rec_buff=10000, max_docs=None, lex_name="new_lexicon"):
	logging.debug("start make lexicon")
	
	if not isinstance(input_dataset, cm.DataSet):
		input_dataset = cm.DataSet.objects.get(id=input_dataset)
	if not output_dataset:
		output_dataset = input_dataset
	if max_docs:
		documents = input_dataset.sample_set.order_by("?")[0:max_docs]
	else:
		documents = input_dataset.sample_set.order_by("?")

	logging.debug("init workers pool")
	pool = Pool(workers)
	text_buff = []
	docs_handled = 0
	term_dict = dict()


	logging.debug("creating lexicon")
	doc_size = documents.count()
	lexicon, created = am.Lexicon.objects.get_or_create(name=lex_name,
		doc_size=doc_size, dataset=output_dataset)
	lexicon.doc_size = doc_size
	if not created:
		lexicon.save()
	else:
		to_be_deleted = am.Token.objects.filter(lexicon=lexicon)
		logging.debug("remove %d old tokens" % to_be_deleted.count())
		to_be_deleted.delete()


	docs_handled = 0
	star_time = datetime.datetime.now()
	logging.debug("tokenizing documents")
	for doc in documents.iterator():
		
		docs_handled += 1
		text_set = (doc.title, "", doc.content,)
#		text_set = (doc.title, doc.summary, doc.content,)
		text_buff.append(text_set)

		if len(text_buff) > buff_size:
			counters = pool.map(count_terms, text_buff)
			recount_terms(term_dict, counters)
			text_buff = []
			gc.collect()

			elapsed = (datetime.datetime.now() - star_time).seconds
			logging.debug("\t :: {0:2.2f}%\t {1} / {2}\t worktime {3} sec\t ave speed {4:0.2f} d / sec".format(
				float(docs_handled * 100) / float(doc_size),
				doc_size,
				docs_handled,
				elapsed,
				float(docs_handled) / float(elapsed)
			))

	
	counters = pool.map(count_terms, text_buff)
	recount_terms(term_dict, counters)
	text_buff = []
	pool.close()
	gc.collect()


	token_cache = []
	logging.debug("saving %s terms" % len(term_dict))
	for term, tag, nertag, origin, tfreq, dfreq in term_dict.itervalues():
		t = am.Token(
			lexicon = lexicon,
			postag = tag,
			nertag = nertag,
			text = term,
			origin = origin,
			tfreq = tfreq,
			dfreq = dfreq,
			rfreq = float(dfreq) / doc_size
		)
		token_cache.append(t)
		if len(token_cache) > rec_buff:
			am.Token.objects.bulk_create(token_cache)
			logging.debug("%s terms flushed" % len(token_cache))
			token_cache = []
			gc.collect()
	am.Token.objects.bulk_create(token_cache)
	logging.debug("%s terms flushed" % len(token_cache))
	token_cache = []
	gc.collect()

	logging.debug("DONE")


def recount_terms(term_dict, counters):
	for counter in counters:
		for k in counter:
			token, tag, nertag, origin, freq = counter[k]
			term = term_dict.get(k)
			if term:
				_, _, _, _, old_freq, old_dferq = term
				term_dict[k] = (token, tag, nertag, origin, old_freq + freq, old_dferq + 1)
			else:
				term = (token, tag, nertag, origin, freq, 1)
				term_dict[k] = term