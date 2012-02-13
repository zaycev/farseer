# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
import  datetime
from analyzer.preproc import search

def index(request):
	years = xrange(2008,2013)
	months = xrange(1,13)
	today = datetime.datetime.now()
	return render_to_response("index.html", {
		"years": years,
		"months": months,
		"today": today,
	})


def analyze(request):

	query = request.GET["text_query"]
	start_year = int(request.GET["start_year"])
	start_month = int(request.GET["start_month"])
	end_year = int(request.GET["end_year"])
	end_month = int(request.GET["end_month"])
	group_size = int(request.GET["group_size"])
	min_views = int(request.GET["min_views"])
	min_comments = int(request.GET["min_comments"])


#	positions = dict()

	timerange = search.time_range(
		(start_year, start_month),
		(end_year, end_month),
		group_size,
	)

	cur_point = timerange[0]
	results = []
	rank_cache = []

	for next_point in timerange[1:len(timerange)]:


		result = search.search(query,min_comments,min_views,cur_point,next_point,16,rank_cache)
		cur_point = next_point

#		if result["subset"]:
#			new_rank = []
#			for row in result["data"]:
#				if row["term"] in positions:
#					row["delta"] = positions[row["term"]] - row["idx"]
#				else:
#					row["delta"] = 0
#				positions[row["term"]] = row["idx"]
#				new_rank.append(row)
#			results.append({
#				"subset":-1,#result["subset"],
#				"data":new_rank,
#				"start":cur_date,
#				"end":next_date,
#				"result":{
#				}
#			})

		results.append(result)

	return render_to_response("analyze.html", {
		"query": query,
		"results": results,
	})
