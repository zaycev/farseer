# -*- coding: utf-8 -*-
from collector.core.worker import WkHtmlFetcher

FB_URI_PATTERN = u"http://graph.facebook.com/{0}"									# Facebook
TW_URI_PATTERN = u"http://urls.api.twitter.com/1/urls/count.json?url={0}"			# Twitter
TP_URI_PATTERN = u"http://otter.topsy.com/stats.js?url={0}"							# Topsy
SU_URI_PATTERN = u"http://www.stumbleupon.com/services/1.01/badge.getinfo?url={0}"	# StumbleUpon
LI_URI_PATTERN = u"http://www.linkedin.com/cws/share-count?url={0}"					# LinkedIn
DG_URI_PATTERN = u"http://widgets.digg.com/buttons/count?url={0}"					# Digg
GP_URI_PATTERN = None																# GooglePlus

SC_URI_PATTERN = u"http://api.sharedcount.com/?url={0}"								# SocialCounter

class WkSNDataFetcher(WkHtmlFetcher):
	name = "worker.abstract_social_fetcher"
	template = None

	def target(self, task, **kwargs):
		pass
	#uri = task.job.uri

class WkFbFetcher(WkHtmlFetcher):
	pass

class WkTwFetcher(WkHtmlFetcher):
	pass

class WkTpFetcher(WkHtmlFetcher):
	pass

class WkSuFetcher(WkHtmlFetcher):
	pass

class WkDgFetcher(WkHtmlFetcher):
	pass

class WkGpFetcher(WkHtmlFetcher):
	pass

class WkLiFetcher(WkHtmlFetcher):
	pass

class WkScFetcher(WkHtmlFetcher):
	pass