# -*- coding: utf-8 -*-
from collector.models import DocumentSource
from lxml.html import fromstring
from datetime import timedelta
from time import strftime
import datetime

BUNDLE_KEY = "F.INV"
BUNDLE_NAME = "Forbes Blogs / Investing"


def get_or_create_source():
	source, created = DocumentSource.objects.get_or_create(
		name = BUNDLE_NAME,
		key = BUNDLE_KEY,
		url = "http://www.forbes.com/investing/",
	)
	if not created:source.save()
	return source


def __daterange__(start_date, end_date):
	for n in range((end_date - start_date).days):
		yield start_date + timedelta(n)

PROBE_HOURS = ("00:00:01", "04:00:00",
			   "08:00:00", "12:00:00",
			   "16:00:00", "20:00:00",
			   "23:00:00")
REQUEST_URL_PAT =  "http://www.forbes.com/investing/more?" \
				   "publishdate=%s %s&offset=0&limit="
def make_river_link_iterator(start, length):
	start_date = datetime.datetime.now() - timedelta(start)
	end_date = start_date - timedelta(length)
	for date in __daterange__(end_date, start_date):
		for probe_time in PROBE_HOURS:
			probe_date = strftime("%m/%d/%Y", date.timetuple())
			yield REQUEST_URL_PAT % (probe_date, probe_time)


LINK_SPOT_XPATH = "/html/body/div[2]/div[3]/div[1]/div[1]/div/div/div/article/div[2]/header/div[2]/a/@href"
def spot_links(html):
	tree = fromstring(html)
	paths = tree.xpath(LINK_SPOT_XPATH)
	return ["http://www.lookatme.ru%s" % article_path for article_path in paths]