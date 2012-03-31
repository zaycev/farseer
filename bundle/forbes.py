# -*- coding: utf-8 -*-
from io import StringIO
from collector.models import DocumentSource
from lxml import etree
from lxml.html import fromstring
from datetime import timedelta
from time import strftime
import traceback
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

XPATH_TITLE = "/html/head/title/text()"
RE_TITLE = re.compile("(.+)\s+- Forbes.*")
RE_EMPTY = re.compile("\s+")
RE_DATE_1 = re.compile("\s*([0-9\\/]+).*@\s*([0-9\\:APMpm]+)\s*")
RE_DATE_2 = re.compile("(\d\d\\.\d\d\\.\d\d).+(\d\d\\:\d\d [APMapm]{2})")
def extract_essential(rawdoc):
	tree = fromstring(rawdoc.body)
	try:
		title = re.findall(RE_TITLE, tree.xpath(XPATH_TITLE)[0])[0]
	except Exception:
		title = None
	author_url = tree.xpath("id('abovefold')/div/div[1]/div[2]/p[1]/a/@href")
	if not author_url: author_url = tree.xpath("id('storyBody')/cite/a/@href")

	try:
		try:
			if "forbes.com/sites/" in rawdoc.url:
				body_el = tree.find_class("body")
			else:
				body_el = tree.find_class("lingo_region")
			body_el = body_el[0]
			body = "\n".join([e.xpath("string()")
							  for e in body_el if e.tag == "p"])
		except Exception: body = None
		if not body:
			try:
				body_el = tree.get_element_by_id("intro")
				body = body_el.xpath("string()")
			except Exception: body = None
		if not body:
			try:
				body_el = tree.find_class("body")[0]
				p_els = body_el.findall(".//p")
				body = "\n".join([p.xpath("string()") for p in p_els])

			except Exception: body = None
	except Exception: body = None
	if body: body = re.sub(RE_EMPTY, " ", body)
	try:
		date_str = tree.xpath("id('abovefold')/div/div[1]/hgroup/h6/text()")[0]
		dt_tuple = re.findall(RE_DATE_1, date_str)[0]
		published = datetime.datetime.strptime("%s %s" % dt_tuple, '%m/%d/%Y %I:%M%p')
	except Exception:
		try:
			date_str = tree.xpath("id('storyBody')/span/text()")[0]
			dt_tuple = re.findall(RE_DATE_2, date_str)[0]
			published = datetime.datetime.strptime("%s %s" % dt_tuple, '%m.%d.%y %I:%M %p')

		except Exception:
			published = None
	return {
		"title": title,
		"author_url": author_url if author_url else [],
		"content": body,
		"published": published if published else None
	}