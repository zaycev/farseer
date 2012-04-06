# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response

from search.models import SToken
from search.models import SDocument

def index(request):
	id_query = request.GET.get("id")
	tx_query = request.GET.get("tx")

	if not id_query and not tx_query:
		token = SToken.objects.get(id=496803)
	elif id_query:
		token = SToken.objects.get(id=int(id_query))
	else:
		token = SToken.search(tx_query)[0]
	return render_to_response("search/index.html", {
		"token": token,
	})