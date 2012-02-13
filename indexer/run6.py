# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from options import DATABASE_CONFIG
from distr.nlp import WkRefiner
import csv
import math


CSV_TFIDF = "/Volumes/HFS/research/tfidf.csv"
CSV_DICT = "/Volumes/HFS/research/dict_30p_20q_l2_l32_reindexed.csv"
CSV_DICT2 = "/Volumes/HFS/research/dict_stop_filtered.csv"

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
	tid, term, total_freq, doc_freq, rel_doc_freq = r
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

MIN_VIEWS = 0
MIN_COMMENTS = 0

proxy = connection.execute("SELECT id,term FROM stop_list")

stoplist = set()

for id, term in proxy:
	stemmed_token = ref.stem(term)
	stoplist.add(term)
proxy.close()

import re
r = re.compile(".*[0-9]+.*")

file_dict = open(CSV_DICT2, "w")
COLUMNS = "id,term,total_freq,doc_freq,rel_doc_freq\n"
PATTERN = u"{0},\"{1}\",{2},{3},{4:f}\n"
file_dict.write(COLUMNS)
for tid, term, total_freq, doc_freq, rel_doc_freq in dict1:
	if term not in stoplist and not r.match(term):
		file_dict.write(PATTERN\
		.format(tid, term, total_freq, doc_freq, rel_doc_freq)\
		.encode('UTF-8'))
file_dict.close()

