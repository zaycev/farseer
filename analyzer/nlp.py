# -*- coding: utf-8 -*-

from analyzer.tagger import make_tagger

from nltk import TreebankWordTokenizer
from nltk.data import load
from nltk.tag import _POS_TAGGER
from nltk.chunk import _MULTICLASS_NE_CHUNKER
from nltk.tokenize import PunktSentenceTokenizer

import logging
import pickle
import gc

UTIL = None
term_cache = None

class NlpUtil(object):

	def __init__(self):
		self.wrd_tokenizer = TreebankWordTokenizer()
		self.snt_tokenizer = PunktSentenceTokenizer()
		self.pos_tagger = pickle.load(open("tagger.pickle", "r"))
		self.ner_tagger = load(_MULTICLASS_NE_CHUNKER)

	def wrd_tokenize(self, text):
		snts = self.snt_tokenizer.tokenize(text)
		word_tokens = []
		for s in snts:
			word_tokens.extend(self.wrd_tokenizer.tokenize(s))
		return word_tokens
		# return self.wrd_tokenizer.tokenize(text)

	def pos_tag(self, tokens):
		tagged = self.pos_tagger.tag(tokens)
		new_tagged = []
		for word, tag in tagged:
			if tag is None:
				new_tagged.append((word, "?"))
			else:
				new_tagged.append((word, tag))
		return new_tagged

	def ner_tag(self, tagged_tokens):
		return self.ner_tagger.parse(tagged_tokens)
		
	def tokenize(self, text):
		tokens = self.wrd_tokenize(text)
		pos_tagged = self.pos_tag(tokens)
		ner_tagged = self.ner_tag(pos_tagged)
		return ner_tagged

def make_util():
	global UTIL
	if not UTIL: UTIL = NlpUtil()
	return UTIL

def count_terms(text_set):
	util = make_util()
	counter = dict()
	# counter : key -> (<token>, <tag>, <ner_tag>, <freq>)
	for text in text_set:
		tokens = util.tokenize(text)

		for token in tokens:
			if type(token) is tuple:
				# handle non NER chunk
				token, tag = token[0].lower(), token[1].lower()
				token_key = token+tag
				nertag = None
				origin = None
			else:
				# handle NER chunk, considering tree has height equal to 1
				nertag = token.node.lower()
				tokens = token.leaves()
				origin = " ".join([t[0] for t in tokens])
				tokens.sort(key=lambda e: e[0])
				tokens = [(e[0].lower(), e[1].lower(),) for e in tokens]
				token, tag = tokens[0]
				for tk, tg in tokens[1:len(tokens)]:
					token += "+" + tk
					tag += "+" + tg
				token_key = "ner" + token + tag
			if token_key not in counter:
				counter[token_key] = (token, tag, nertag, origin, 1)
			else:
				prev_count = counter[token_key][4]
				counter[token_key] = (token, tag, nertag, origin, prev_count + 1)

	gc.collect()
	return counter