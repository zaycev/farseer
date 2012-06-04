# -*- coding: utf-8 -*-
from multiprocessing import Pool

from search.models import SDocument
from collector.models import DataSet
from collector.models import Probe
from collector.sm import tw_probe

# from collector.tw import do_it
# do_it()

import logging


def work(url):
	repeats = 0
	probe = None
	while not probe and repeats < 10:
		try:
			probe = tw_probe(url)
			return probe, url
		except Exception:
			probe = None
			logging.debug("exception %s" % repeats)
			repeats += 1
	return -1, url


def do_it():

	ds = DataSet.objects.get(id=15)

	docs = SDocument.objects.count()

	pool = Pool(16)
	url_buff = []
	docs_handled = 0

	logging.debug("start fetching probes")

	for doc in SDocument.objects.values("url").iterator():

		docs_handled += 1
		url_buff.append(doc["url"])

		if len(url_buff) > 256:
			probes = pool.map(work, url_buff)
			url_buff = []
			new_probes = []
			for s, u in probes:
				new_probes.append(
					Probe(
						target = u,
						dataset = ds,
						tag = "tw",
						signal = s,
				))
			Probe.objects.bulk_create(new_probes)
			logging.debug("%s\t/\t%s" % (docs_handled, docs))

	logging.debug("DONE")




