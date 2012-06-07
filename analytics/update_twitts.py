# -*- coding: utf-8 -*-
from multiprocessing import Pool
from threading import RLock
import time

from analytics.models import Sample
from collector.models import DataSet
from collector.sm import tw_probe

# from collector.tw import do_it
# do_it()
#from analytics.update_twitts import do_it

import logging


def work(input_data):
	doc_id, url = input_data
	repeats = 0
	signal = -1
	while signal==-1 and repeats < 32:
		try:
			signal = tw_probe(url)
		except Exception:
			logging.debug("exception %s" % repeats)
			repeats += 1
	return doc_id, signal
	


def do_it():

	ds = DataSet.objects.get(id=15)

	samples = ds.sample_set.count()
	
	all_outputs = []

	pool = Pool(64)
	input_buff = []
	s_handled = 0

	logging.debug("start fetching probes")

	for sample in ds.sample_set.values("id", "url").iterator():

		s_handled += 1
		input_buff.append((sample["id"], sample["url"]))

		if len(input_buff) >= 512:
			outputs = pool.map(work, input_buff)
			input_buff = []
			
			all_outputs.extend(outputs)
			
			logging.debug("%s\t/\t%s" % (s_handled, samples))
			time.sleep(10)

	outputs = pool.map(work, input_buff)
	all_outputs.extend(outputs)
	logging.debug("%s\t/\t%s" % (s_handled, samples))

	logging.debug("COLLECTING DONE")
	
	for s_id, signal in all_outputs:
		s = Sample.objects.get(id=s_id)
		old_signal = s.twits
		s.twits = signal
		s.save()
		print "sample updated %s: %s -> %s" % (s_id, old_signal, signal)