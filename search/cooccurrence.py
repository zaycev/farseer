# -*- coding: utf-8 -*-

from django.db import connection
from search.models import SDocument
from search.models import SToken

class SCooccurrence(object):

	def __init__(self, token, max_coo=128):
		self.__coo_list = coocurences(token)[0:max_coo]

	def other(self):
		for coo in self.__coo_list:
			if not self._is_person_(coo)\
			and not self._is_location_(coo)\
			and not self._is_org_(coo)\
			and not self._is_facility_(coo):
				yield self._wrap_(coo)

	def people(self):
		for coo in self.__coo_list:
			if self._is_person_(coo):
				yield self._wrap_(coo)

	def orgs(self):
		for coo in self.__coo_list:
			if self._is_org_(coo):
				yield self._wrap_(coo)

	def locations(self):
		for coo in self.__coo_list:
			if self._is_location_(coo):
				yield self._wrap_(coo)

	def facilities(self):
		for coo in self.__coo_list:
			if self._is_facility_(coo):
				yield self._wrap_(coo)

	def _is_person_(self, coo):
		return coo[4] == "person"

	def _is_org_(self, coo):
		return coo[4] == "organization"

	def _is_location_(self, coo):
		return coo[4] == "location" or  coo[4] == "gpe" or coo[4] == "gsp"

	def _is_facility_(self, coo):
		return coo[4] == "facility"

	def _wrap_(self, row):
		tid, text, score, postag, nertag = row
		return {
			"id": tid,
			"text": text,
			"score": score,
			"postag": postag,
			"nertag": nertag,
		}



#	def orgs(self):
#		for tid, text, score in self.__coo_list:





SQL = """SELECT	t1.document_id as did, t1.token_id as tid,
		t1.tfidf as score, t2.vi as vi,
		t3.origin as text1, t3.text as text2,
		t3.postag as postag, t3.nertag as nertag
FROM 	search_svector as t1,
		search_sdocument as t2,
		search_stoken as t3
WHERE t1.document_id IN
	(SELECT id FROM search_sdocument
	WHERE fts @@ plainto_tsquery('english',%s)
	ORDER BY vi DESC LIMIT 128)
	AND t1.document_id = t2.id
	AND t1.token_id = t3.id
ORDER BY tid, vi;"""

def coocurences(query):
	if isinstance(query, SToken):
		query = query.visible_text
		#documents = SDocument

	cursor = connection.cursor()
	cursor.execute(SQL, (query,))
	rows = cursor.fetchall()
	cursor.close()

	terms = []
	prev_term = None
	for did, tid, score, vi, t1, t2, postag, nertag in rows:
		if prev_term and prev_term[0] != tid:
			terms.append(prev_term)
			prev_term = None
		if not prev_term:
			text = t1 if t1 else t2
			prev_term = [tid, text, score, postag, nertag]
		else:
			prev_term[2] += score
	

	terms.sort(key = lambda x: x[2])
	terms.reverse()

	return terms