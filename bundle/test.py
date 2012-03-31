#-*- coding: utf-8 -*-

import sys
import bundle
import logging
import unittest
import collector.models as cm

TEST_SETS_DIR = bundle.DEFAULT_DIR

class BundleTest(unittest.TestCase):

	def test_spot_links(self):
		log = logging.getLogger( "BundleTest" )
		for b, river in bundle.iterate_test_objects(cm.RawRiver):
			if hasattr(b, "spot_links"):
				links = b.spot_links(river.body)
				log.debug("bundle %s spot_links river#%s -> %s links" % (b.BUNDLE_KEY, river.id, len(links)))
				self.assertTrue(len(links) > 0)

	def test_extract_title(self):
		log = logging.getLogger( "BundleTest" )
		for b, rawdoc in bundle.iterate_test_objects(cm.RawDocument):
			if hasattr(b, "extract_essential"):
				try:
					title = b.extract_essential(rawdoc).get("title")
					log.debug("bundle %s extract_title rawdoc#%s -> %s" % (b.BUNDLE_KEY, rawdoc.id, title))
					self.assertTrue(title is not None)
				except Exception:
					print(rawdoc.id)

	def test_extract_author(self):
		log = logging.getLogger( "BundleTest" )
		errors = .0
		objects = .0
		for b, rawdoc in bundle.iterate_test_objects(cm.RawDocument):
			if hasattr(b, "extract_essential"):
				author_url = b.extract_essential(rawdoc).get("author_url")
				log.debug("bundle %s author_url rawdoc#%s -> %s" % (b.BUNDLE_KEY, rawdoc.id, author_url))
				if not author_url or len(author_url) < 0:
					errors += 1
				objects += 1
		logging.debug("ERR:%s;\t OBJ:%s" % (errors, objects))
		self.assertLess(errors / objects, 0.05)


	def test_extract_body(self):
		log = logging.getLogger( "BundleTest" )
		errors = .0
		objects = .0
		for b, rawdoc in bundle.iterate_test_objects(cm.RawDocument):
			if hasattr(b, "extract_essential"):
				body = b.extract_essential(rawdoc).get("body")
				log.debug("bundle %s body_text rawdoc#%s -> %s ... (%s)"
					% (b.BUNDLE_KEY, rawdoc.id, body[0:32]
						if body else None, len(body) if body else 0))
				if not body or len(body) < 0:
					errors += 1
				objects += 1
		logging.debug("ERR:%s;\t OBJ:%s" % (errors, objects))
		self.assertLess(errors / objects, 0.05)

	def test_extract_body(self):
		log = logging.getLogger( "BundleTest" )
		errors = .0
		objects = .0
		for b, rawdoc in bundle.iterate_test_objects(cm.RawDocument):
			if hasattr(b, "extract_essential"):
				published = b.extract_essential(rawdoc).get("published")
				log.debug("bundle %s published rawdoc#%s -> %s"
					% (b.BUNDLE_KEY, rawdoc.id, published))
				if not published:
					errors += 1
				objects += 1
		logging.debug("ERR:%s;\t OBJ:%s" % (errors, objects))
		self.assertLess(errors / objects, 0.05)


logging.basicConfig(stream=sys.stderr)
logging.getLogger("BundleTest").setLevel(logging.DEBUG)