# -*- coding: utf-8 -*-

from analyzer.model import db_session, db_engine
from analyzer.model import TaggedTerm
from prettytab import pprint_table
import analyzer.nlp as nlp
import datetime

import sys
import math


def key_words(doc_id):
	db_conn = db_engine.connect()


	if not nlp.term_cache:
		nlp.term_cache = dict()
		for term in db_session.query(TaggedTerm).order_by("nertag").yield_per(4096):
			nlp.term_cache[term.id] = term

	term_cache = nlp.term_cache

	doc_vec = []
	vec_ids = []
	prev_id = None
	weight = (
		0.6,
		0.3,
		0.1,
	)

	start = datetime.datetime.now()

	for fid,tid,count in db_conn.execute("SELECT fid,tid,count FROM set_docterm WHERE did={0} ORDER BY tid;".format(doc_id)):
		if tid != prev_id:
			doc_vec.append(0)
			vec_ids.append(tid)
			prev_id = tid
		doc_vec[-1] += count * weight[fid]
	db_conn.close()

	for i in xrange(len(doc_vec)):
		doc_vec[i] *= math.log(float(1 / term_cache[vec_ids[i]].rfreq), 1.2)


	vec_len = math.sqrt(sum([x**2 for x in doc_vec]))
	doc_ver = zip(vec_ids, doc_vec)

	doc_ver.sort(key = lambda x: x[1])
	doc_ver.reverse()

	res_size = 32
	sys.stdout.write("\n\n")
	print ":: time ~ {0:0.3f} ms".format(float((datetime.datetime.now() - start).microseconds) / 1000)
	pprint_table(sys.stdout,
		[["#", "term", "tf", "idf", "tfidf", "norm_tfidf", "nertag"]]+
		[["", "", "", "", "", "", ""]]+
		[[	str(i),
			term_cache[doc_ver[i][0]].term,
			"{0:0.8f}".format(doc_ver[i][1] * math.log(float(1 / term_cache[doc_ver[i][0]].rfreq))),
			"{0:0.8f}".format(math.log(float(1 / term_cache[doc_ver[i][0]].rfreq))),
			"{0:0.8f}".format(doc_ver[i][1]),
			"{0:0.8f}".format(doc_ver[i][1] / vec_len),
			term_cache[doc_ver[i][0]].nertag
			] for i in xrange(res_size if len(doc_ver) >= res_size else len(doc_ver))]
	)
	sys.stdout.write("\n\n")
	sys.stdout.flush()


def load_term_cache(session):
	term_cache = dict()
	for term in session.query(TaggedTerm).order_by("nertag").all():
		term_cache[term.id] = term
	return term_cache


def analyze(text_query):

	if not nlp.term_cache:
		nlp.term_cache = load_term_cache(db_session)
	term_cache = nlp.term_cache

	db_conn = db_engine.connect()
	prev_time_id = None
	median_data = None

#	"views",
	data_fields = [
		("score", "Score", lambda a, b: a + b),
#		("fb_shr", "Facebook", lambda a, b: a + b),
#		("su", "StumbleUpon", lambda a, b: a + b),
#		("dg", "Digger", lambda a, b: a + b),
#		("li", "LinkedIn", lambda a, b: a + b),
#		("time", "Timestamp", lambda a, b: b),
#		("month_id", "Month ID", lambda a, b: b),
	]
	key_field = "month_id"

	order_by = "month_id"

	GET_DOCS_SQL = u"SELECT {0},{1} FROM set_corpora WHERE fts @@ to_tsquery('{2}') ORDER BY {1};".format(
		",".join([field[0] for field in data_fields]),
		order_by,
		text_query
	)
	#data_fields.append(order_by)

	data_field_series = [[] for _ in xrange(len(data_fields))]
	prev_order_id = None
	for row in db_conn.execute(GET_DOCS_SQL.format(text_query)):
		row = tuple(row)
		if row[-1] != prev_order_id:
			prev_order_id = row[-1]

			for ser in data_field_series:
				ser.append(0)

		for i in xrange(len(data_field_series)):
			prev_val = data_field_series[i][-1]
			data_field_series[i][-1] = data_fields[i][2](prev_val, row[i])

	data_series = {
		"key" if data_fields[i][0] == key_field else data_fields[i][0]:{
			"name": data_fields[i][1],
			"data":data_field_series[i],
		}
		for i in xrange(len(data_fields))
	}

	print data_field_series


	return {
		"doc_stat": data_series,
	}





if __name__ == "__main__":
	analyze(sys.argv[1])





#url = URL(
#	db["repository"]["driver"],
#	username=db["repository"]["user"],
#	password=db["repository"]["password"],
#	host=db["repository"]["host"],
#	port=db["repository"]["port"],
#	database=db["repository"]["database"]
#)
#db_engine = create_engine(url)
#connection = db_engine.connect()
#
#terms = []
#term_map = dict()
#for row in connection.execute("SELECT * FROM features ORDER BY tid ASC;"):
#	terms.append(row)
#	term_map[row[1]] = row[0]
#lexicon_size = len(terms)
#
#sql_score =	u"SELECT tid,tfidf "\
#			u"FROM scores WHERE did IN "\
#				u"(SELECT id FROM news " \
#				u"WHERE time>='{0}-{1}-1' AND time<'{2}-{3}-1' " \
#				u"AND news_fts_col @@ to_tsquery('english','{4}') "\
#				u"ORDER BY views DESC  LIMIT 100) " \
#			u"ORDER BY tid;"
#
#sql_pow =	u"SELECT id,time,title,views,short_text "\
#			u"FROM news "\
#			u"WHERE news_fts_col "\
#				u"@@ to_tsquery('english','{4}') "\
#				u"AND time>='{0}-{1}-1' AND time<'{2}-{3}-1' "\
#			u"ORDER BY views DESC LIMIT 100;"
#
#sql_docs_count = u"SELECT count(id) FROM news " \
#				u"WHERE news_fts_col "\
#					u"@@ to_tsquery('english','{4}') "\
#					u"AND time>='{0}-{1}-1' AND time<'{2}-{3}-1';"\
#
##sql_stat = "SELECT id,views,coms FROM"
#
#def time_range(start, end, delta):
#	time_range = []
#	current = start
#	time_range.append(current)
#	while True:
#		if current[1] + delta > 12:
#			current = (current[0]+1, current[1] + delta - 12)
#		else:
#			current = (current[0], current[1] + delta)
#		time_range.append(current)
#		if current >= end:
#			return time_range
#
#def search(
#		text_query,
#		start_date,
#		end_date,
#		max_set,
#		prev_ranks):
#
#
#	query= sql_score.format(
#					start_date[0], start_date[1],
#		  			end_date[0], end_date[1],
#		  			text_query)
#
#	query_get_docs_count = sql_docs_count.format(
#		start_date[0], start_date[1],
#		end_date[0], end_date[1],
#		text_query
#	)
#
#	exc = connection.execute(query_get_docs_count)
#	for x in exc:
#		docs_count = x[0]
#
#
##	prev_tid=0
##	prev_tfidf=0.0
#	tfidf_acc = [0]*lexicon_size
#
#	for tid,tfidf in connection.execute(query):
#		tfidf_acc[tid] += tfidf
##		if tid != prev_tid:
##			tfidf_acc.append((tid,tfidf))
##			prev_tfidf = 0.0
##		prev_tfidf += tfidf
##		prev_tid = tid
#
#
#	ranks = list(xrange(lexicon_size))
#
#	if len(prev_ranks) is 0:
#		for i in xrange(lexicon_size):
#			prev_ranks.append(ranks[i])
#
#	ranks.sort(key=lambda x: tfidf_acc[x], reverse=True)
#
#	result = []
#
#
#	x = 1
#	for tid in ranks[0:max_set]:
#		result.append({
#			"idx":x,
#			"term":terms[tid][1],
#			"score":tfidf_acc[tid],
#			"comms":0,
#			"views":0,
#			"delta":prev_ranks[tid] - x + 1,
#		})
#		x += 1
#
#	for i in xrange(lexicon_size):
#		prev_ranks[ranks[i]] = i
#
#	return {
#		"time": {
#			"start":  datetime.datetime(start_date[0], start_date[1], 1),
#			"end":  datetime.datetime(end_date[0], end_date[1], 1),
#		},
#		"subset_size": docs_count,
#		"data": result,
#	}