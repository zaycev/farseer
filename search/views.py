# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.shortcuts import HttpResponse

from search.models import SToken
from search.models import SDocument
from search.cooccurrence import SCooccurrence

import json

def index(request):
	id_query = request.GET.get("id")
	tx_query = request.GET.get("tx")
	if not id_query and not tx_query:
		token = SToken.objects.get(id=496803)
		related = token.related()
	elif id_query:
		token = SToken.objects.get(id=int(id_query))
		related = token.related()
	else:
		token = None
		try:
			related = SToken.search(tx_query)[0].related()
		except Exception:
			related = None
	return render_to_response("search/index.html", {
		"token": token,
		"related": related,
		"token_text": token.visible_text if token else tx_query,
		"cooccurrences": SCooccurrence(token if token else tx_query),
	})


def get_popular(request):
	q1 = request.GET.get("q1", "")
	q2 = request.GET.get("q1", "")
	popular = SDocument.search_popular(q1, q2)
	return HttpResponse(json.dumps(list(popular)), content_type="application/json")