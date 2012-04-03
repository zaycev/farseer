# -*- coding: utf-8 -*-

import unittest
import logging

from analyzer.nlp import make_util
from analyzer.lexicon import make_lexicon
from collector.models import DataSet

class NlpUtilTest(unittest.TestCase):

	def test_make_util(self):

		util = make_util()
		self.assertIsNotNone(util)


	def test_tokenize(self):

		text = \
		"Last week, I wrote a post about the deepening doubts many climate scientists"\
		"have expressed about democracy’s ability to avert dangerous climate change."\
		"These “doubts” have manifested themselves first and foremost in growing support"\
		"for federally-funded geoengineering research, which has attracted significant"\
		"support as a result of the perceived failure of climate-change negotiations in"\
		"Copenhagen in 2008. The flood of vitriol I received in response to my post from"\
		"both sides of the hockey-stick has convinced me of the desperate need for some"\
		"basic rules-of-engagement for discussing global warming.  To this end, I have"\
		"formulated the following four suggestions for discussing global warming more"\
		"productively.   (Note: the title alludes to George Orwell’s essay, “Politics and"
		"the English Language“) 1."

		util = make_util()
		tokens = util.tokenize(text)
		self.assertTrue(len(tokens) > 0)

		logging.debug(len(tokens))


	# def test_make_lexicon(self):

	# 	ds = DataSet.objects.get(id=15)

	# 	term_dict = make_lexicon(ds)