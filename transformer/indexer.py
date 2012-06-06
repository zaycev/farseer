# -*- coding: utf-8 -*-

import gc
import logging
import datetime
import transformer.nlp as nlp
import collector.models as cm
import transformer.models as tm
import analytics.models as am
from multiprocessing import Pool
from transformer.nlp import count_voc_terms
from transformer.nlp import make_vocab



def index_dataset(input_dataset, lexicon, workers=4,
	buff_size=256, max_docs=None):
	

	logging.debug("start make index")
	if not isinstance(input_dataset, cm.DataSet):
		input_dataset = cm.DataSet.objects.get(id=input_dataset)
	if not isinstance(lexicon, tm.Lexicon):
		lexicon = tm.Lexicon.objects.get(id=lexicon)
	if max_docs:
		documents = input_dataset.sample_set.order_by("?")[0:max_docs]
	else:
		documents = input_dataset.sample_set.order_by("?")
	doc_size = documents.count()

	
	vocab = make_vocab(tm.Token.objects.filter(lexicon=lexicon))
	logging.debug("loaded %s tokens from lexicon" % len(vocab))


	logging.debug("init workers pool")
	pool = Pool(workers, lambda: cache_vocab(vocab))
	text_buff = []
	docs_buff = dict()
	docs_handled = 0

	star_time = datetime.datetime.now()
	logging.debug("tokenizing documents")
	for doc in documents.iterator():
		
		docs_handled += 1
		text_set = (doc.id, (("T", doc.title), ("C", doc.content),))
		text_buff.append(text_set)
		docs_buff[doc.id] = doc

		if len(text_buff) > buff_size:
			
			output = pool.map(count_voc_terms, text_buff)
			save_terms(output, docs_buff, vocab)
			text_buff = []
			docs_buff = dict()
			gc.collect()

			elapsed = (datetime.datetime.now() - star_time).seconds
			logging.debug("\t :: {0:2.2f}%\t {1} / {2}\t worktime {3} sec\t ave speed {4:0.2f} d / sec".format(
				float(docs_handled * 100) / float(doc_size),
				doc_size,
				docs_handled,
				elapsed,
				float(docs_handled) / float(elapsed + 0.001)
			))
	
	output = pool.map(count_voc_terms, text_buff)
	save_terms(output, docs_buff, vocab)
	pool.close()
	gc.collect()



def cache_vocab(vocab):
	nlp.VOCB = vocab



def save_terms(worker_output, doc_buff, vocab):
	terms = []
	for doc_id, counters in worker_output:
		for fid, counter in counters:
			for tkey, tfreq in counter:
				term = am.Term(
					token = vocab[tkey],
					sample = doc_buff[doc_id],
					field = fid,
					freq = tfreq,
				)
				terms.append(term)
	am.Term.objects.bulk_create(terms)






