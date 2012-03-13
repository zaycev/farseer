# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from options import DATABASE_CONFIG
from distr.nlp import WkRefiner
import csv
import math


CSV_TFIDF = "/Volumes/HFS/research/tfidf.csv"
CSV_DICT = "/Volumes/HFS/research/dict_stop_filtered_30p_20q_reindexed.csv"


csv.register_dialect("farseer", delimiter=',', quotechar='"')


#DOCS = 3
#TERMS = 5000
TERMS_COUNTER = 0

dict_file = open(CSV_DICT, "rb")
dict_csv = csv.reader(dict_file, "farseer")
dict_csv.next()
dict1 = list()
dict2 = dict()
for r in dict_csv:
	tid,term,total_freq,doc_freq,rel_doc_freq = r
	tid = int(tid)
	total_freq = int(total_freq)
	doc_freq = int(doc_freq)
	rel_doc_freq = float(rel_doc_freq)
	dict1.append((tid, term, total_freq, doc_freq, rel_doc_freq))
	dict2[term] = tid
	TERMS_COUNTER += 1
#	if TERMS_COUNTER > TERMS:
#		break

dict_file.close()
TERMS = len(dict1)
#for r in dict1:
#	print r[0],r[1]
#print "\n"

url = URL(
	DATABASE_CONFIG["DB_DRIVER"],
	username=DATABASE_CONFIG["DB_USER"],
	password=DATABASE_CONFIG["DB_PASSWORD"],
	host=DATABASE_CONFIG["DB_HOST"],
	port=DATABASE_CONFIG["DB_PORT"],
	database=DATABASE_CONFIG["DB_DATABASE"])
db_engine = create_engine(url)
db_metadata = MetaData(bind=db_engine)
connection = db_engine.connect()
ref = WkRefiner()

import sys
print "\n\n"

proxy = connection.execute("select id,post_views_qti,post_comments_qti,full_text,post_title,post_short_text from task_topic_raw WHERE id={0}".format(sys.argv[1]))
for did,views_q, comments_q, text, short, title in proxy:
	stemmed = ref.tokenize(text)
	stemmed_s = ref.tokenize(short)
	stemmed_t = ref.tokenize(title)

	DOC_SIZE = 0.0
	TFIDF = [0]*TERMS

	for t in stemmed:
		tid = dict2.get(t, -1)
		if tid is not -1:
			TFIDF[tid] += .2
			DOC_SIZE += .2

	for t in stemmed_s:
		tid = dict2.get(t, -1)
		if tid is not -1:
			TFIDF[tid] += .3
			DOC_SIZE += .3

	for t in stemmed_t:
		tid = dict2.get(t, -1)
		if tid is not -1:
			TFIDF[tid] += .5
			DOC_SIZE += .5


	if DOC_SIZE > 0:
		for i in xrange(0, TERMS):
			IDF = dict1[i][4]
			TFIDF[i] = float(TFIDF[i]) / DOC_SIZE / math.log(1 / IDF, 2)

	if DOC_SIZE > 0:
		NORM = math.sqrt(sum([comp**2 for comp in TFIDF]))
		for i in xrange(0, TERMS):
			TFIDF[i] /= NORM

	RANKED = [(i, TFIDF[i]) for i in xrange(0, TERMS) if TFIDF[i] > 0]

	RANKED.sort(key=lambda x: x[1], reverse=True)

	x = 0
	for i, tfidf in RANKED[0:32]:
		print "{0}\t{1}     \t {2:f}".format(x,dict1[i][1], tfidf)
		x += 1

	print "\n\n"


proxy.close()