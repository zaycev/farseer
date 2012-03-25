# -*- coding: utf-8 -*-
from collector.models import DocumentSource
from lxml.html import fromstring

BUNDLE_KEY = "LAM"
BUNDLE_NAME = "Look At Me"


def get_or_create_source():
	source, created = DocumentSource.objects.get_or_create(
		name = BUNDLE_NAME,
		key = BUNDLE_KEY,
		url = "http://www.lookatme.ru/",
	)
	if not created:source.save()
	return source


def make_river_link_iterator(start, length):
	for page in xrange(start, start + length):
		yield "http://www.lookatme.ru/flow?page=%s" % page


LINK_SPOT_XPATH = "/html/body/div[2]/div[3]/div[1]/div[1]/div/div/div/article/div[2]/header/div[2]/a/@href"
def spot_links(html):
	tree = fromstring(html)
	paths = tree.xpath(LINK_SPOT_XPATH)
	return ["http://www.lookatme.ru/%s" % article_path for article_path in paths]