# -*- coding: utf-8 -*-

#from analyzer.lexicon import LexiconTerm

DEFAULT_WEIGHT_SCHEMA = (
	#	input table			tf-idf
	# 	column name			weight
	("title",			0.5),
	("short_text",		0.4),
	("full_text",		0.1),
)


class SelectionRule(object):
	def __init__(self):
		self.triggered = 0
	def apply(self, lexicon_term):
		pass

def selection(input_table_name="set_lexicon",
			  output_table_name="set_features"):
	pass