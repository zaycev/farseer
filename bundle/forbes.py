# -*- coding: utf-8 -*-
from collector.models import DocumentSource
from lxml.html import fromstring
from datetime import timedelta
from time import strftime
import datetime
import re


BUNDLE_KEY = "FORBES"
BUNDLE_NAME = "Forbes Blogs / All"


def get_or_create_source():
	source, created = DocumentSource.objects.get_or_create(
		name = BUNDLE_NAME,
		key = BUNDLE_KEY,
		url = "http://www.forbes.com/",
	)
	if not created:source.save()
	return source


SITE_SECTIONS = (
	"business",
	"investing",
	"technology",
	"entrepreneurs",
	"leadership",
	"lifestyle",
	"lists",
)
PROBE_HOURS = ("00:00:01", "04:00:00",
			   "08:00:00", "12:00:00",
			   "16:00:00", "20:00:00",
			   "23:00:00")
REQUEST_URL_PAT =  "http://www.forbes.com/%s/more?" \
				   "publishdate=%s %s&offset=0&limit="
def rivers_count(_, length):
	return length * len(PROBE_HOURS) * len(SITE_SECTIONS)
def __daterange__(start_date, end_date):
	for n in range((end_date - start_date).days):
		yield start_date + timedelta(n)
def make_river_link_iterator(start, length):
	start_date = datetime.datetime.now() - timedelta(start)
	end_date = start_date - timedelta(length)
	for date in __daterange__(end_date, start_date):
		for probe_time in PROBE_HOURS:
			for section in SITE_SECTIONS:
				probe_date = strftime("%m/%d/%Y", date.timetuple())
				yield REQUEST_URL_PAT % (section, probe_date, probe_time)


LINK_SPOT_XPATH = "li/article/hgroup/h2/a/@href"
def spot_links(html):
	tree = fromstring(html)
	return set(tree.xpath(LINK_SPOT_XPATH))

TITLE_XPATH = "/html/head/title/text()"
TITLE_RE = re.compile("(.+)\s+- Forbes.*")
import traceback
def extract_essential(rawdoc):
	tree = fromstring(rawdoc.body)
	try:
		title = re.findall(TITLE_RE, tree.xpath(TITLE_XPATH)[0])[0]
	except Exception:
		print traceback.format_exc()
		title = None
	return {
		"title": title,

	}