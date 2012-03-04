# -*- coding: utf-8 -*-

from nltk import TreebankWordTokenizer
from nltk.data import load
from nltk.tag import _POS_TAGGER
from nltk.chunk import _MULTICLASS_NE_CHUNKER
from nltk.tokenize import PunktSentenceTokenizer
import re

util = None
term_cache = None

class NlpUtil(object):

	def __init__(self):
		self.wrd_tokenizer = TreebankWordTokenizer()
		self.snt_tokenizer = PunktSentenceTokenizer()
		self.snt_corrector = SentenceCorrector()
		self.pos_tagger = load(_POS_TAGGER)
		self.ner_tagger = load(_MULTICLASS_NE_CHUNKER)

	def tokenize(self, text):
		snts = self.snt_tokenizer.tokenize(text)
		csnts = self.snt_corrector.correct(snts)
		word_tokens = []
		for s in csnts:
			word_tokens.extend(self.wrd_tokenizer.tokenize(s))
		return word_tokens

	def pos_tag(self, tokens):
		return self.pos_tagger.tag(tokens)

	def ner_tag(self, tagged_tokens):
		return self.ner_tagger.parse(tagged_tokens)



class SentenceCorrector():

	def __init__(self):
		self.pattern = re.compile("([a-z0-9][" + re.escape(".!?") + "]+[A-Z])")

	def correct(self, bad_formed_sentences):
		new_sentences = []
		for snt in bad_formed_sentences:
			split_idxs = [m.end()  - 1 for m in re.finditer(self.pattern, snt)]
			if split_idxs:
				prev = 0
				for idx in split_idxs:
					new_sentences.append(snt[prev:idx])
					prev = idx
				new_sentences.append(snt[prev:len(snt)])
			else:
				new_sentences.append(snt)
		return new_sentences