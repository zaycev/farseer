# -*- coding: utf-8 -*-

from search.models import SDocument, SToken
from django.db import connection
from django.db import transaction
from math import log, sqrt


# from search.tfidf import update_tfidf
# update_tfidf()

def update_tfidf():
	docs = SDocument.objects.values("id").all()
	
	
	tokens = {token.id:token for token in SToken.objects.all()}


	DSIZE = 50980
	handled = 0

	icursor = connection.cursor()
	ocursor = connection.cursor()


	for doc in docs:

		tfidf_vec = compute_vec(icursor, doc["id"], DSIZE, tokens)
		handled += 1
		# print doc.id, doc.title
		# pprint_vec(tfidf_vec)

		save_vec(ocursor, doc["id"], tfidf_vec)

		if handled % 256 == 0:
			print "\t%s\t/\t%s" % (DSIZE, handled)


	transaction.commit_unless_managed()
	icursor.close()
	ocursor.close()

		# cursor = connection.cursor()
		# for tid, fid, tfidf in nterms:
		# 	cursor.execute("UPDATE search_sterm SET tfidf=%s WHERE document_id=%s AND token_id=%s AND field=%s;", [tfidf, ])


def compute_vec(cursor, did, corpus_size, token_dict):
	cursor.execute("SELECT token_id,field,freq FROM "\
					"search_sterm WHERE document_id=%s;", (did,))
	rows = cursor.fetchall()
	doc_size = sum([r[2] for r in rows])
	terms = {}
	for tid, fid, freq in rows:
		if tid not in terms:
			terms[tid] = compute_tfidf(	freq, doc_size,
										corpus_size, token_dict[tid],
										fid)
		else:
			terms[tid] = compute_tfidf(	freq, doc_size,
										corpus_size, token_dict[tid],
										fid)
	terms = terms.items()
	doc_len = sqrt(sum([tfidf ** 2 for _,tfidf in terms]))
	nterms = [(tid, tfidf / doc_len) for tid, tfidf in terms]
	return nterms


def compute_tfidf(freq, doc_size, corpus_size, token, fid):
	koef = 0.1
	if token.nertag:
		koef *= 5
		if token.nertag == "person" or token.nertag == "organization":
			koef *= 2
	else:
		if "nn" in token.postag or "np" in token.postag:
			koef *= 3
	if fid == "T":
		koef *= 3
	return koef * float(freq) / doc_size  *  log(corpus_size / token.dfreq)


def pprint_vec(vec):
	vec = vec[:]
	vec.sort(key=lambda x: x[1])
	vec.reverse()

	for tid, tfidf in vec[0:16]:
		token = SToken.objects.get(id=tid)
		print "%s - %s" % (token.visible_text, tfidf)
	print


def save_vec(cursor, doc_id, vec):
	for tid, tfidf in vec:
		cursor.execute("INSERT INTO search_svector VALUES (%s,%s,%s);",
				(doc_id, tid, tfidf))





