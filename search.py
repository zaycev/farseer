# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from options import DATABASE_CONFIG as db
import datetime


url = URL(
	db["repository"]["driver"],
	username=db["repository"]["user"],
	password=db["repository"]["password"],
	host=db["repository"]["host"],
	port=db["repository"]["port"],
	database=db["repository"]["database"]
)
db_engine = create_engine(url)
connection = db_engine.connect()

terms = []
term_map = dict()
for row in connection.execute("SELECT * FROM features ORDER BY tid ASC;"):
	terms.append(row)
	term_map[row[1]] = row[0]
lexicon_size = len(terms)
sql_score =	u"SELECT tid,tfidf "\
			u"FROM scores WHERE did IN "\
				u"(SELECT id FROM news " \
				u"WHERE time>='{0}-{1}-1' AND time<'{2}-{3}-1' " \
				u"AND news_fts_col @@ to_tsquery('english','{4}') "\
				u"AND comms>{5} AND views>{6}) " \
			u"ORDER BY tid;"
#sql_stat = "SELECT id,views,coms FROM"

def time_range(start, end, delta):
	time_range = []
	current = start
	time_range.append(current)
	while True:
		if current[1] + delta > 12:
			current = (current[0]+1, current[1] + delta - 12)
		else:
			current = (current[0], current[1] + delta)
		time_range.append(current)
		if current >= end:
			return time_range

def search(
		text_query,
		min_comments,
		min_views,
		start_date,
		end_date,
		max_set,
		prev_ranks):


	query= sql_score.format(
					start_date[0], start_date[1],
		  			end_date[0], end_date[1],
		  			text_query, min_comments, min_views)

	prev_tid=0
	prev_tfidf=0.0
	tfidf_acc = [0]*lexicon_size

	for tid,tfidf in connection.execute(query):
		tfidf_acc[tid] += tfidf
#		if tid != prev_tid:
#			tfidf_acc.append((tid,tfidf))
#			prev_tfidf = 0.0
#		prev_tfidf += tfidf
#		prev_tid = tid


	ranks = list(xrange(lexicon_size))

	if len(prev_ranks) is 0:
		for i in xrange(lexicon_size):
			prev_ranks.append(ranks[i])

	ranks.sort(key=lambda x: tfidf_acc[x], reverse=True)

	result = []


	x = 1
	for tid in ranks[0:max_set]:
		result.append({
			"idx":x,
			"term":terms[tid][1],
			"score":tfidf_acc[tid],
			"comms":0,
			"views":0,
			"delta":prev_ranks[tid] - x + 1,
		})
		x += 1

	for i in xrange(lexicon_size):
		prev_ranks[ranks[i]] = i

	return {
		"time": {
			"start":  datetime.datetime(start_date[0], start_date[1], 1),
			"end":  datetime.datetime(end_date[0], end_date[1], 1),
		},
		"subset_size": -1,
		"data": result,
	}