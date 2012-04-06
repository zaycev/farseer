# -*- coding: utf-8 -*-

from search.models import SDocument
from search.models import SToken

from django.db import connection


# from search.coocurence import coocurences


SQL = """SELECT	t1.document_id as did, t1.token_id as tid,
		t1.field as fid, t1.freq as tfreq,
		t3.rfreq as rfreq, t2.vi as vi,
		t3.origin as text1, t3.text as text2
FROM 	search_sterm as t1,
		search_sdocument as t2,
		search_stoken as t3
WHERE t1.document_id IN
	(SELECT id FROM search_sdocument
	WHERE fts @@ plainto_tsquery('english',%s)
	ORDER BY vi DESC LIMIT 32)
	AND t1.document_id = t2.id
	AND t1.token_id = t3.id
ORDER BY tid, field, freq;"""

def coocurences(query):
	if isinstance(query, SToken):
		query = query.visible_name
		#documents = SDocument

	cursor = connection.cursor()
	cursor.execute(SQL, (query,))
	rows = cursor.fetchall()
	cursor.close()

	terms = []
	prev_term = None
	for did, tid, fid, tfreq, rfreq, vi, t1, t2 in rows:
		if prev_term and prev_term[0] != tid:
			terms.append(prev_term)
			prev_term = None
		if not prev_term:
			text = t1 if t1 else t2
			prev_term = [tid, did, text, tfidf(tfreq, rfreq, fid)]
		else:
			prev_term[3] += tfidf(tfreq, rfreq, fid)
	

	terms.sort(key = lambda x: x[3])
	terms.reverse()

	return terms[0:32]




def tfidf(tfreq, rfreq, field):
	return tfreq * rfreq