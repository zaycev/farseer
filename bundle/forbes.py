# -*- coding: utf-8 -*-
from io import StringIO
from collector.models import DocumentSource
from lxml import etree
from lxml.html import fromstring
from datetime import timedelta
from time import strftime
import collector.sm as sm
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
	"lists",)
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


XPATH_VIEWS = "id('abovefold')/div/div[1]/hgroup/h6[2]/text()"
RE_VIEWS = re.compile("(\d+)\,?(\d+)\s+views")
def _extract_views(tree):
	views_str = tree.xpath(XPATH_VIEWS)
	if views_str:
		try:
			if isinstance(views_str, list) and len(views_str) == 2:
				views = re.findall(RE_VIEWS, views_str[1])[0]
				views = int(views[0] + views[1])
				return views
			elif isinstance(views_str, list) and len(views_str) == 1:
				views = re.findall(RE_VIEWS, views_str[0])[0]
			else:
				views = re.findall(RE_VIEWS, views_str)[0]
			return int(views)
		except: return -1
	else: return -1
XPATH_COMMENTS = "id('abovefold')/div/div[1]/div[3]/div[3]/div[2]/a/text()"
RE_COMMENTS = re.compile("\s*(\d+)\s+.+\s+(\d+)\s+called.+\s*")
def _extract_comments(tree):
	comments_str = tree.xpath(XPATH_COMMENTS)
	if comments_str:
		comments = re.findall(RE_COMMENTS, comments_str[0])[0]
		return int(comments[0]), int(comments[1])
	else: return -1, -1
def get_probes(raw_document):
	# print raw_document.url
	tree = fromstring(raw_document.body)
	# fb_resp = sm.fb_probe(raw_document.url)
	# tw_resp = sm.tw_probe(raw_document.url)
	# su_resp = sm.su_probe(raw_document.url)
	# li_resp = sm.li_probe(raw_document.url)
	# dg_resp = sm.dg_probe(raw_document.url)
	comments = _extract_comments(tree)
	return {
		"vi": _extract_views(tree),
		"co": comments[0] + comments[1] if comments[0] > 0 else 0,
		"c1": comments[0],
		"c2": comments[1],
		# "fb": fb_resp[0] + fb_resp[1],
		# "fs": fb_resp[0],
		# "fc": fb_resp[1],
		# "tw": tw_resp,
		# "su": su_resp,
		# "li": li_resp,
		# "dg": dg_resp,
	}









