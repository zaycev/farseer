# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from options import DATABASE_CONFIG
from apps.nlp import WkRefiner
import csv
import math


CSV_TFIDF = "/Volumes/HFS/research/tfidf.csv"
CSV_DICT = "/Volumes/HFS/research/dict_30p_100q_reindex.csv"


csv.register_dialect("farseer", delimiter=',', quotechar='"')


#DOCS = 1000
#TERMS = 20
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
TERMS = TERMS_COUNTER
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

file_tfidf = open(CSV_TFIDF,"w")

file_tfidf.write("doc_id,doc_vq,doc_cq")
for i in xrange(0, TERMS):
	file_tfidf.write(",t"+str(i))
file_tfidf.write("\n")

proxy = connection.execute("select id,post_views_qti,post_comments_qti,full_text from task_topic_raw ORDER BY id")
for did,views_q, comments_q, text in proxy:

	file_tfidf.write(str(did))
	file_tfidf.write(",")
	file_tfidf.write(str(views_q))
	file_tfidf.write(",")
	file_tfidf.write(str(comments_q))

	stemmed = ref.tokenize(text)

	DOC_SIZE = 0.0
	TFIDF = [0]*TERMS
	for t in stemmed:
		tid = dict2.get(t, -1)
		if tid is not -1:
			TFIDF[tid] += 1
			DOC_SIZE += 1
	if DOC_SIZE > 0:
		for i in xrange(0, TERMS):
			IDF = dict1[i][4]
			TFIDF[i] = float(TFIDF[i]) / DOC_SIZE / math.log(1 / IDF, 2)

	if DOC_SIZE > 0:
		NORM = math.sqrt(sum([comp**2 for comp in TFIDF]))
		for i in xrange(0, TERMS):
			TFIDF[i] /= NORM

	for i in xrange(0, TERMS):
		file_tfidf.write(",{0:f}".format(TFIDF[i]))
	file_tfidf.write("\n")


#	print(*TFIDF)


	#,[t for t in stemmed if t in dict2]
#	print "\n"

#	print [t for t in stemmed if t in dict2]

proxy.close()