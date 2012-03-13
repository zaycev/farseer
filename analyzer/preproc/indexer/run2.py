# -*- coding: utf-8 -*-

from sqlalchemy import Integer, Text, Float, Boolean, Binary, MetaData
from sqlalchemy import Table, create_engine
from sqlalchemy.orm import mapper, create_session
from sqlalchemy.engine.url import URL

from options import DATABASE_CONFIG
from distr.nlp import WkRefiner


CSV_DICT = "/Volumes/HFS/research/dict.csv"
CSV_PROB = "/Volumes/HFS/research/prob.csv"
CSV_RESP = "/Volumes/HFS/research/resp.csv"

DOCS = 5000

ref = WkRefiner()

TERM_COUNTER = 0
DOC_COUNTER = 0

INDEXED_TERMS = dict()
INDEXED_TERMS2 = dict()
TF = []
IDF = dict()

import datetime
print datetime.datetime.now()

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
count_p = connection.execute("select count(id) from task_topic_raw")
count = 0
for row in count_p:
	count = row[0]
proxy = connection.execute("select id,post_views_qti,post_comments_qti,full_text from task_topic_raw ORDER BY post_time".format(DOCS))


#file_resp = open(CSV_RESP,"w")
#file_resp.write("id,views,comments,len\n")
for doc_id, views_q, comments_q, text in proxy:
	stemmed = ref.tokenize(text)
#	file_resp.write("{0},{1},{2},{3}\n".format(doc_id,views_q,comments_q,len(stemmed)))
	DOC_COUNTER += 1
	TF.append(dict())
	for st in stemmed:
		if st not in INDEXED_TERMS:
			TERM_ID = TERM_COUNTER
			INDEXED_TERMS[st] = TERM_ID
			INDEXED_TERMS2[TERM_ID] = st
			TERM_COUNTER += 1
			IDF[TERM_ID] = dict()
		else:
			TERM_ID = INDEXED_TERMS[st]
		if TERM_ID in TF[-1]:
			TF[-1][TERM_ID] += 1
		else:
			TF[-1][TERM_ID] = 1
			if doc_id in IDF[TERM_ID]:
				IDF[TERM_ID][doc_id] += 1
			else:
				IDF[TERM_ID][doc_id] = 1
#file_resp.close()

connection.close()

#file_dict = open(CSV_DICT,"w")
#COLUMNS = "id,term,total_freq,doc_freq,rel_doc_freq\n"
#PATTERN = u"{0},\"{1}\",{2},{3},{4:f}\n"
#file_dict.write(COLUMNS)
#keys = INDEXED_TERMS2.keys()
#keys.sort()
#SELECTED = set()
#for i in xrange(0, len(keys)):
#	id = i
#	term = INDEXED_TERMS2[i]
#	doc_occurrences = [doc[id] for doc in TF if id in doc]
#	total_freq = sum(doc_occurrences)
#	doc_freq = len(doc_occurrences)
#	rel_doc_freq = float(doc_freq) / float(DOC_COUNTER)
#	if True:
##	if 0.33 > rel_doc_freq and doc_freq > 10:
#		SELECTED.add(id)
#		file_dict.write(PATTERN\
#			.format(id,term,total_freq,doc_freq,rel_doc_freq)\
#				.encode('UTF-8'))
#file_dict.close()

#file_prob = open(CSV_PROB,"w")
#selected = list(SELECTED)
#selected.sort()
#file_prob.write(",")
#for id in selected:
#	file_prob.write(u",{0}".format(id).encode('UTF-8'))
#file_prob.write("\n,")
#for id in selected:
#	file_prob.write(u",\"{0}\"".format(INDEXED_TERMS2[id]).encode('UTF-8'))
#file_prob.write("\n")
#for id1 in selected:
#	D1 = [doc_id for doc_id in xrange(0, len(TF)) if id1 in TF[doc_id]]
#	FLEN = float(len(D1))
#	file_prob.write(u"{0},\"{1}\"".format(id1,INDEXED_TERMS2[id1]).encode('UTF-8'))
#	for id2 in selected:
#		D2 = [doc_id for doc_id in xrange(0, len(TF)) if id2 in TF[doc_id]]
#		INTERSECT = set(D1).intersection(set(D2))
#		PROB = float(len(INTERSECT)) / FLEN
#		file_prob.write(",{0:f}".format(PROB))
#	file_prob.write("\n")
#
#file_prob.close()

print datetime.datetime.now()