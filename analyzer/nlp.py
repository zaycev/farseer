# -*- coding: utf-8 -*-

from nltk import WordPunctTokenizer
from nltk import pos_tag
from nltk import word_tokenize
from nltk.tag import DefaultTagger

def make_tokenizer():
	return WordPunctTokenizer()

def make_tagger():
	return DefaultTagger()

def assign_tags(tokens):
	return [(token.lower(), tag) for token, tag in pos_tag(tokens)]

Tokenizer = None
Tagger = None