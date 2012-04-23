# -*- coding: utf-8 -*-

from analyzer.tagger import make_tagger
from nltk import TreebankWordTokenizer
from nltk.chunk import _MULTICLASS_NE_CHUNKER
from nltk.tokenize import PunktSentenceTokenizer
from nltk.data import load
import nltk.tag

import logging
import pickle
import gc


UTIL = None
VOCB = None


class NlpUtil(object):

	def __init__(self):
		self.wrd_tokenizer = TreebankWordTokenizer()
		self.snt_tokenizer = PunktSentenceTokenizer()
		self.pos_tagger = pickle.load(open("tagger.pickle", "r"))
		self.ner_tagger = load(_MULTICLASS_NE_CHUNKER)

	def wrd_tokenize(self, text):
		return self.wrd_tokenizer.tokenize(text)

	def pos_tag(self, tokens):
		tagged = self.pos_tagger.tag(tokens)
		new_tagged = []
		for word, tag in tagged:
			if tag is None:
				new_tagged.append((word, "-NONE-"))
			else:
				new_tagged.append((word, tag))
		return new_tagged

	def ner_tag(self, tagged_tokens):
		return self.ner_tagger.parse(tagged_tokens)
		
	def tokenize(self, text):
		snts = self.snt_tokenizer.tokenize(text)
		for s in snts:
			tokens = self.wrd_tokenize(s)
			pos_tagged = self.pos_tag(tokens)
			ner_tagged = self.ner_tag(pos_tagged)
			for nt in ner_tagged:
				yield nt


def make_util():
	global UTIL
	if not UTIL: UTIL = NlpUtil()
	return UTIL


def make_vocab(tokens_query):
	vocab = dict()
	for t in tokens_query.iterator():
		tkey = make_term_key(t.text, t.postag, t.nertag)
		vocab[tkey] = t
	return vocab


def count_terms(text_set):
	util = make_util()
	counter = dict()
	# counter : key -> (<token>, <tag>, <ner_tag>, <freq>)
	for text in text_set:
		tokens = util.tokenize(text)
		for token in tokens:
			if type(token) is tuple:
				# handle non-NER chunk
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


def count_voc_terms(doc_data):
	doc_id, text_fields = doc_data
	# maps (fid, text) -> {tkey: count}
	global VOCB
	output = []
	for fid, text in text_fields:
		counter = count_terms((text,))
		reduced_counter = list()#dict()
		for tk in counter.values():
			tkey = make_term_key(tk[0], tk[1], tk[2])
			if tkey in VOCB:
				if tkey in reduced_counter:
					print "ERROR", tkey
				# reduced_counter[tkey] = tk[4]
				reduced_counter.append((tkey, tk[4]))
		output.append((fid, reduced_counter,))
	return (doc_id, output,)


def make_term_key(text, postag, nertag):
	return u"%s-%s-%s" % (str(nertag), str(postag), text)