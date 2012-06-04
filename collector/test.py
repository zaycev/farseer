#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from collector.workers import TextFetcher

TEXT_FETCHER_URL = "http://python.org"
class TextDataFetcherTest(unittest.TestCase):

	def test_init(self):
		fetcher = TextFetcher()
		self.assertEqual(type(fetcher), TextFetcher)
		self.assertEqual(fetcher._encoding, "utf-8")

	def test_fetch_text(self):
		fetcher = TextFetcher()
		text = fetcher.fetch_text(TEXT_FETCHER_URL)
		self.assertEqual(type(text), unicode)
		self.assertTrue(len(text) > 0)