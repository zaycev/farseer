# -*- coding: utf-8 -*-

from json import loads
import urllib

def _fetch(url):
	return urllib.urlopen(url).read()


def fb_probe(url):
	json = _fetch(u"http://graph.facebook.com/%s" % url)
	resp = loads(json)
	return resp.get("shares", 0), resp.get("comments", 0)


def tw_probe(url):
	url = u"http://urls.api.twitter.com/1/urls/count.json?url=%s" % url
	json = _fetch(url)
	resp = loads(json)
	return resp.get("count", 0)


def su_probe(url):
	json = _fetch(u"http://www.stumbleupon.com/"\
					"services/1.01/badge.getinfo?url=%s" % url)
	resp = loads(json)
	return int(resp.get("result", {"views":0}).get("views", 0))


def li_probe(url):
	url = u"http://www.linkedin.com/cws/share-count?url=%s" % url
	json = _fetch(url)
	print "ok, got"
	resp = loads(json[26:len(json)])
	return resp.get("count", 0)


def dg_probe(url):
	json = _fetch(u"http://widgets.digg.com/buttons/count?url=%s" % url)
	resp = loads(json[19:-2])
	return resp.get("diggs", 0)