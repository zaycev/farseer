#-*- coding: utf-8 -*-

import sys
import bundle
import logging
import unittest
import collector.models as cm

TEST_SETS_DIR = "bundle/test"

class TextDataFetcherTest(unittest.TestCase):

	def test_spot_links(self):
		log = logging.getLogger( "TextDataFetcherTest" )
		for b, river in bundle.iterate_test_objects(cm.RawRiver):
			if hasattr(b, "spot_links"):
				links = b.spot_links(river.body)
				log.debug("bundle %s spot_links river#%s -> %s links" % (b.BUNDLE_KEY, river.id, len(links)))
				self.assertTrue(len(links) > 0)

	def test_extract_title(self):
		log = logging.getLogger( "TextDataFetcherTest" )
		for b, rawdoc in bundle.iterate_test_objects(cm.RawDocument):
			if hasattr(b, "extract_essential"):
				title = b.extract_essential(rawdoc).get("title")
				log.debug("bundle %s extract_title rawdoc#%s -> %s" % (b.BUNDLE_KEY, rawdoc.id, title))
				self.assertTrue(title is not None)


logging.basicConfig(stream=sys.stderr)
logging.getLogger("TextDataFetcherTest").setLevel(logging.DEBUG)