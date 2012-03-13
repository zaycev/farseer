# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from analyzer.model import db_session, TaggedTerm, Document
from sqlalchemy import func

import search

def index(request):

	people = db_session.query(TaggedTerm).filter(TaggedTerm.nertag == "person").order_by("-dfreq")
	locations = db_session.query(TaggedTerm).filter(TaggedTerm.nertag == "location").order_by("-dfreq")
	organizations = db_session.query(TaggedTerm).filter(TaggedTerm.nertag == "organization").order_by("-dfreq")
	facilities = db_session.query(TaggedTerm).filter(TaggedTerm.nertag == "facility").order_by("-dfreq")
	randoms = db_session.query(TaggedTerm).order_by("RANDOM()")

	stories = db_session.query(Document).order_by("-score")[0:32]


	return render_to_response("index.html", {
		"termsets": {
			"properties": [
					{"name":"people", "count":db_session.query(func.count("*")).select_from(TaggedTerm).filter(TaggedTerm.nertag=="person").scalar()},
					{"name":"locations", "count":db_session.query(func.count("*")).select_from(TaggedTerm).filter(TaggedTerm.nertag=="location").scalar()},
					{"name":"organizations", "count":db_session.query(func.count("*")).select_from(TaggedTerm).filter(TaggedTerm.nertag=="organization").scalar()},
					{"name":"facilities", "count":db_session.query(func.count("*")).select_from(TaggedTerm).filter(TaggedTerm.nertag=="facility").scalar()},
					{"name":"random"},
			],
			"data": zip( people[0:32], locations[0:32], organizations[0:32], facilities[0:32], randoms[0:32]),
		},
		"stories": stories,
	})


def result(request):
	text_query = request.GET["q"]
	result = search.analyze(text_query)
	return render_to_response("result.html", {
		"result": result,
		"query": text_query,
	})
