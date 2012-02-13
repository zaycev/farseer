# -*- coding: utf-8 -*-

import math
import sys
import csv

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from options import DATABASE_CONFIG
from distr.nlp import WkRefiner

ref = WkRefiner()


url = URL(
	DATABASE_CONFIG["DB_DRIVER"],
	username=DATABASE_CONFIG["DB_USER"],
	password=DATABASE_CONFIG["DB_PASSWORD"],
	host=DATABASE_CONFIG["DB_HOST"],
	port=DATABASE_CONFIG["DB_PORT"],
	database=DATABASE_CONFIG["DB_DATABASE"])
db_engine = create_engine(url)
connection = db_engine.connect()

terms = []
term_map = dict()
lexicon_size = 0

for row in connection.execute("SELECT * FROM features ORDER BY tid ASC;"):
	terms.append(row)
	term_map[row[1]] = row[0]
	lexicon_size += 1


#corpus_size = 136217

connection.execute("DELETE FROM scores;")
connection.execute("DELETE FROM doc_stat;")

for did,full,short,title,coms,views in connection.execute("SELECT id,full_text,post_short_text,post_title,post_comments_qti,post_views_qti FROM task_topic_raw ORDER BY id;"):

	full_s = ref.tokenize(full)
	short_s = ref.tokenize(short)
	title_s = ref.tokenize(title)

	doc_float_size = 0.0

	vsm = [0] * lexicon_size
	idx = set()

	for t in full_s:
		tid = term_map.get(t, -1)
		if tid is not -1:
			idx.add(tid)
			vsm[tid] += .2
			doc_float_size += .2

	for t in short_s:
		tid = term_map.get(t, -1)
		if tid is not -1:
			idx.add(tid)
			vsm[tid] += .3
			doc_float_size += .3

	for t in title_s:
		tid = term_map.get(t, -1)
		if tid is not -1:
			idx.add(tid)
			vsm[tid] += .5
			doc_float_size += .5


	if doc_float_size > 0:
		if did % 100 is 0:
			connection.execute("BEGIN;")
		new_vsm = []
		for tid in idx:
			tf = vsm[tid]
			idf = terms[tid][4]
			tfidf = tf * math.log(1 / idf, 2)
			new_vsm.append((tid, tfidf))

		norm = math.sqrt(sum([t[1]**2 for t in new_vsm]))
		new_vsm2 = [(tid, tfidf/norm) for tid, tfidf in new_vsm]
		new_vsm2.sort(key=lambda x: x[1], reverse=True)
#
#		sys.stdout.write("{0} - {1} : ".format(did, len(new_vsm2)))
		for tid, tfidf in new_vsm2:
			connection.execute("INSERT INTO scores (did,tid,tfidf) VALUES ({0},{1},{2:0.16f});".format(did,tid,tfidf))
#			sys.stdout.write("({0}, {1}), ".format(terms[tid][1], tfidf))
#		sys.stdout.write("\n")

		connection.execute("INSERT INTO doc_stat (did,nzeros,coms,views) VALUES ({0},{1},{2},{3});".format(did,len(idx),coms,views))

		if did % 100 is 0:
			connection.execute("COMMIT;")
			print did#, "\n\n"
#		print new_vsm2


#		for i in xrange(0, terms_count):
#			IDF = terms[i][4]
#			tfidf_acc[i] = float(tfidf[i]) / doc_float_size / math.log(1 / IDF, 6)
#		NORM = math.sqrt(sum([comp ** 2 for comp in tfidf]))
#		for i in xrange(0, terms_count):
#			tfidf_acc[i] /= NORM
