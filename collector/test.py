#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from collector.models import DocumentSource
from collector.workers import TextFetching
from collector.workers import RiverFetcher


TEXT_FETCHER_URL = "http://google.com"
class TextDataFetcherTest(unittest.TestCase):

	def test_init(self):
		fetcher = TextFetching()
		self.assertEqual(type(fetcher), TextFetching)
		self.assertEqual(fetcher.encoding, "utf-8")

	def test_fetch_text(self):
		fetcher = TextFetching()
		text = fetcher.fetch_text(TEXT_FETCHER_URL)
		self.assertEqual(type(text), unicode)
		self.assertTrue(len(text) > 0)


RIVER_FETCHER_SOURCE_ID = 1
RIVER_SOURCE_PAGE = 1
class RiverFetcherTest(unittest.TestCase):

	def test_init(self):
		source = DocumentSource.objects.get(id=RIVER_FETCHER_SOURCE_ID)
		fetcher = RiverFetcher(source)
		self.assertEqual(type(fetcher), RiverFetcher)

	def test_fetch_river(self):
		source = DocumentSource.objects.get(id=RIVER_FETCHER_SOURCE_ID)
		fetcher = RiverFetcher(source)
		river = fetcher.fetch_river(RIVER_SOURCE_PAGE)
		self.assertTrue(river.body and river.mime_type)
		self.assertTrue(len(river.body) > 0)
		self.assertEqual(river.mime_type, "text/html")


class RiverFetchingSupervisor(unittest.TestCase):

	def test_init(self):
		pass