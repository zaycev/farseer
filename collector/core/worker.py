# -*- coding: utf-8 -*-
import urllib2
from collector.core.server.service import Worker

FB_URI_PATTERN = u"http://graph.facebook.com/{0}"									# Facebook
TW_URI_PATTERN = u"http://urls.api.twitter.com/1/urls/count.json?url={0}"			# Twitter
TP_URI_PATTERN = u"http://otter.topsy.com/stats.js?url={0}"							# Topsy
SU_URI_PATTERN = u"http://www.stumbleupon.com/services/1.01/badge.getinfo?url={0}"	# StumbleUpon
LI_URI_PATTERN = u"http://www.linkedin.com/cws/share-count?url={0}"					# LinkedIn
DG_URI_PATTERN = u"http://widgets.digg.com/buttons/count?url={0}"					# Digg
GP_URI_PATTERN = None																# GooglePlus

SC_URI_PATTERN = u"http://api.sharedcount.com/?url={0}"								# SocialCounter


class WkUrlFetcher(Worker):
	name = "worker.fetcher"
	fetch_timeout = 45
	def_enc = "utf-8"
	
	def fetch_html(self, uri):
		req = urllib2.urlopen(url=uri, timeout=self.fetch_timeout)
		try:
			content_type = req["content-type"]
			chunks = content_type.split("charset=")
			enc = chunks[-1] if len(chunks) > 0 else self.def_enc
		except:
			enc = self.def_enc
		data = req.read()
		html = unicode(data, enc)
		return html

class WkSocicalDataFetcher(WkUrlFetcher):
	name = "worker.abstract_social_fetcher"
	template = None
	
	def __target__(self, task, **kwargs):
		pass
		#uri = task.job.uri

class WkFbFetcher(WkUrlFetcher):
	pass
class WkTwFetcher(WkUrlFetcher):
	pass
class WkTpFetcher(WkUrlFetcher):
	pass
class WkSuFetcher(WkUrlFetcher):
	pass
class WkDgFetcher(WkUrlFetcher):
	pass
class WkGpFetcher(WkUrlFetcher):
	pass
class WkLiFetcher(WkUrlFetcher):
	pass
class WkScFetcher(WkUrlFetcher):
	pass