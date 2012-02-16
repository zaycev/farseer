# -*- coding: utf-8 -*-
from collector.core.worker import WkTextDataFetcher
from collector_pb2 import DataRSR, DataSR, JobMeta
import json

# Sequentially fetches data from all social networks
# defined above. Takes uri from 'uri' field of input
# task object put and all downloaded data to 'response'
# and 'response_raw' fields (see DataSR and
# DataS and RDataRSR in /collector.proto)

class WkSNDataFetcher(WkTextDataFetcher):
	name = "worker.sn_fetcher"
	template = None
	use_social_counter = False

	fb_uri = u"http://graph.facebook.com/{0}"									# Facebook
	tw_uri = u"http://urls.api.twitter.com/1/urls/count.json?url={0}"			# Twitter
	tp_uri = u"http://otter.topsy.com/stats.js?url={0}"							# Topsy
	su_uri = u"http://www.stumbleupon.com/services/1.01/badge.getinfo?url={0}"	# StumbleUpon
	li_uri = u"http://www.linkedin.com/cws/share-count?url={0}"					# LinkedIn
	dg_uri = u"http://widgets.digg.com/buttons/count?url={0}"					# Digg
	gp_uri = None																# GooglePlus
	sc_uri = u"http://api.sharedcount.com/?url={0}"								# SocialCounter


	def target(self, task, **kwargs):
		uri = task.job.uri
		response = DataSR()
		response_raw = DataRSR
		if self.use_social_counter is False:
			# fetch data
			fb_raw = self.fetch_text(self.fb_uri.format(uri))
			tw_raw = self.fetch_text(self.tw_uri.format(uri))
			tp_raw = self.fetch_text(self.tp_uri.format(uri))
			su_raw = self.fetch_text(self.su_uri.format(uri))
			li_raw = self.fetch_text(self.li_uri.format(uri))
			dg_raw = self.fetch_text(self.dg_uri.format(uri))
			# parse data
			response_raw.fb = fb_raw
			response_raw.tw = tw_raw
			response_raw.tp = tp_raw
			response_raw.su = su_raw
			response_raw.li = li_raw
			response_raw.dg = dg_raw
			# store data
			response.fb = json.loads(fb_raw)["shares"]
			response.tw = json.loads(tw_raw)["count"]
			response.tp = json.loads(tp_raw)["response"]["all"]
			response.su = json.loads(su_raw)["result"].get("views", 0)
			response.li = json.loads(li_raw[26:len(li_raw)])["count"]
			response.dg = json.loads(dg_raw[19:-2])["diggs"]
			task.job.response_raw.CopyFrom(response_raw)
			task.job.response.CopyFrom(response)
		else:
			pass
		print task
		return [task]