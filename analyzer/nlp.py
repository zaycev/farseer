# -*- coding: utf-8 -*-

#from nltk import WordNetLemmatizer
#from nltk import RegexpTokenizer
from nltk import WordPunctTokenizer
from nltk import pos_tag

pattern = r'''(?x)[A-Z]\.)+
|\w+(-\w+)*
|\$?\d+(\.\d+)?%?
|\.\.\.
|[][.,;\"'?():-_`]'''
def make_tokenizer():
	return WordPunctTokenizer()

def assign_tags(tokens):
	return [(token.lower(), tag) for token, tag in pos_tag(tokens)]


#import re
#
#refining_patterns = [("\n?.*\[[0-9]+\]: .*\n?", ""),
#	("\[[0-9]+\]", ""),
#	("[^a-zA-Z0-9-\']", " "),
#	("  *", " ")]
#
#refining_regexes = [re.compile(p) for p, r in refining_patterns]
#tokenizer_pattern = re.compile(u"\W+")
#stemmer = WordNetLemmatizer()
#empty_string = re.compile("^\s*$")
#
#def clean_up(text):
#	for i in xrange(len(refining_regexes)):
#		r = refining_regexes[i]
#		_, replace = refining_patterns[i]
#		text = r.sub(replace, text)
#	text = text.lower()
#	return text
#
#def stem(token):
#	return stemmer.lemmatize(token)
#
#def filter_test(term):
#	return not empty_string.match(term)
#
#def tokenize(text):
#	text = clean_up(text)
#	words = tokenizer_pattern.split(text)
#	return [stemmer.lemmatize(w) for w in words if filter_test(w)]