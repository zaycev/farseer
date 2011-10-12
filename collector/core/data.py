# -*- coding: utf-8 -*-

"""
Copyright 2011 Vladimir Zaytsev <vladimir@zvm.me>

This file is provided to you under the Apache License,
Version 2.0 (the "License"); you may not use this file
except in compliance with the License.  You may obtain
a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

import json
from hashlib import md5
from urllib import request
from lxml.html import parse
from lxml.html import tostring
from lxml.html import document_fromstring
from lxml.html.clean import clean
from farseer.tool.text import clean_text
from farseer.tool.html2text import html2text

class DocFormat:
	XML = 0
	BIN = 1
	ZIP = 2
	LZM = 3

class FarseerDoc:
	
	def __init__(self):
		self._id_gen = md5()
	
	def serialize(self, format=DocFormat.XML):
		pass
	
class WebResourceProvider:
	
	__LINKPAGE_SIZE__ = None
	__PROVIDER_NAME__ = None
	__ROOT_URL__ = None	
	__DIV_TAG__ = "div"
	__H1_TAG__ = "h1"
	__H2_TAG__ = "h2"
	__H3_TAG__ = "h3"
	__A_TAG__ = "a"
	__HREF_ATTR__ = "href"

	def __init__(self):
		self.__name = None
		self.__linkpage_size = 0
	
	@property
	def name(self):
		return self.__PROVIDER_NAME__
	
	@property
	def root_url(self):
		return self.__ROOT_URL__

	@property
	def linkpage_size(self):
		return self.__LINKPAGE_SIZE__
		
	def generate_url(self, skip):
		pass
	
	def verify_url(self, url):
		pass
		
	def download_links(self, url):
		pass
	
	def download_html(self, url):
		req = request.urlopen(url)
		html = req.read().decode("utf8")
		req.close()
		return html
	
	def extract_views(self, doc=None, html=None):
		pass
	
	def extract_title(self, doc=None, html=None):
		pass
	
	def extract_tags(self, doc=None, html=None):
		pass

	def extract_content(self, doc=None, html=None):
		pass
	
class BiWebProvider(WebResourceProvider):
	__LINKPAGE_SIZE__ = 20
	__PROVIDER_NAME__ = "business_insider"
	__ROOT_URL__ = "http://www.businessinsider.com/"

	def __init__(self):
		super().__init__()
		
	__URL_PATTERN__ = "{0}?start={1}"
	def generate_url(self, skip):
		skip += 200
		return self.__URL_PATTERN__.format(self.root_url, skip)
		
	def verify_url(self, url):
		return self.root_url in url
		
	__POST_CLASS__ = "river-post"
	__ITEM_CLASS__ = "river-item"
	def download_links(self, url):
		doc = parse(url).getroot()
		divs, h2s, h3s, links = [], [], [], []
		for e in doc.find_class(self.__POST_CLASS__):
			if e.tag == self.__DIV_TAG__:
				divs.append(e)
		for div in divs:
			h2s.extend([e for e in div if e.tag == self.__H2_TAG__])
		for h2 in h2s:
			new_links = []
			for e in h2:
				if e.tag == self.__A_TAG__:
					links.append(e.attrib[self.__HREF_ATTR__])
		divs = []
		for e in doc.find_class(self.__ITEM_CLASS__):
			if e.tag == self.__DIV_TAG__:
				divs.append(e)
		for div in divs:
			h3s.extend([e for e in div if e.tag == self.__H3_TAG__])
		for h3 in h3s:
			for e in h3:
				if e.tag == self.__A_TAG__:
					links.append(e.attrib[self.__HREF_ATTR__])
		return links

	__VIEWS_CLASS1__ = "fire views"
	__VIEWS_CLASS2__ = "red views"
	__VIEWS_CLASS3__ = "orange views"
	__VIEWS_CLASS4__ = "grey views"
	def extract_views(self, doc=None, html=None):
		if doc == None:
			doc = document_fromstring(html)
		page_views = doc.find_class(self.__VIEWS_CLASS1__)
		if len(page_views) == 0:
			page_views = doc.find_class(self.__VIEWS_CLASS2__)
		if len(page_views) == 0:
			page_views = doc.find_class(self.__VIEWS_CLASS3__)
		if len(page_views) == 0:
			page_views = doc.find_class(self.__VIEWS_CLASS4__)
		if len(page_views) == 1:
			page_views = page_views[0].text
			page_views = page_views.replace(",", "")
			return int(page_views)
		else:
			return 0
		
	__LAYOUT_POST_CLASS__ = "sl-layout-post"
	def extract_title(self, doc=None, html=None):
		if doc == None:
			doc = document_fromstring(html)
		title = ""
		try:
			for h1 in doc.find_class(self.__LAYOUT_POST_CLASS__):
				for elem in h1:
					if elem.tag == self.__H1_TAG__:
						return clean_text(elem.text_content())
		except:
			return ""
	
	__TAGS_CLASS__ = "tags"
	def extract_tags(self, doc=None, html=None):
		try:
			tag_text = ""
			tags = doc.find_class(self.__TAGS_CLASS__)[0]
			tags = [t for t in tags if t.tag == self.__A_TAG__]
			tags = tags[0:len(tags) - 1]
			for t in tags:
				tag_text += t.text_content() + " "
			return clean_text(tag_text)
		except:
			return ""
	
	__POST_CONTENT_CLASS__ = "post-content"
	def extract_content(self, doc=None, html=None):
		if doc == None:
			doc = document_fromstring(html)
		try:
			content = doc.find_class(self.__POST_CONTENT_CLASS__)[0]
			html = tostring(content, pretty_print=True)
			html = html.decode("utf-8")
			return clean_text(html2text(html))
		except:
			return ""


# WebResourceProvider
# @summary: 
# @status: 
# @todo:
class SocialStatProvider:

	__PROVIDER_NAME__ = None
	__ATTRS__ = None
	
	def __init__(self):
		self.__name = None
		
	@property
	def name(self):
		return self.__PROVIDER_NAME__

	def _download_html(self, url):
		req = request.urlopen(url)
		html = req.read().decode("utf8")
		req.close()
		return html
	
	def _parse_json_(self, json_string):
		return json.loads(json_string)

	def download_raw(self, target):
		pass
	
	def raw_to_dict(self, raw_data):
		dict1, dict2 = self._parse_json_(raw_data), {}
		for attr in self.__ATTRS__:
			if attr in dict1:
				dict2[attr] = dict1[attr]
			else:
				dict2[attr] = 0
		return dict2		

# FbStatProvider
# @summary: 
# @status: 
# @todo:
class FbStatProvider(SocialStatProvider):
	
	__PROVIDER_NAME__ = "facebook"
	__ATTRS__ = ["likes", "shares", "comments"]
	
	__REQ_PATTERN__ = "http://graph.facebook.com/{0}"
	def download_raw(self, target):
		url = self.__REQ_PATTERN__.format(target)
		return self._download_html(url)


# TwStatProvider
# @summary: 
# @status: 
# @todo:
class TwStatProvider(SocialStatProvider):
	
	__PROVIDER_NAME__ = "twitter"
	__ATTRS__ = ["count"]
	
	__REQ_PATTERN__ = "http://urls.api.twitter.com/1/urls/count.json?url={0}"
	def download_raw(self, target):
		url = self.__REQ_PATTERN__.format(target)
		return self._download_html(url)
	
	
class TfIdfDoc(FarseerDoc):
	pass


NEWS_PROVIDERS = [BiWebProvider()]
SOCIAL_PROVIDERS = [FbStatProvider(), TwStatProvider()]
