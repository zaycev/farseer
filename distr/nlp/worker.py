# -*- coding: utf-8 -*-

from collector.core import Worker

#from nltk import LancasterStemmer
#from nltk import PorterStemmer
from nltk import WordNetLemmatizer

import re

refining_patterns = [("\n?.*\[[0-9]+\]: .*\n?", ""),
	("\[[0-9]+\]", ""),
	("\'", ""),
	("[" + re.escape("~`@#$%^&*()_-+={[]}|\:;<,>.?!/") + "]", " "),
	('[\"\!]', " "),
	("[\n\t]", " "),
	("  *", " ")]

refining_regexes = [re.compile(p) for p, r in refining_patterns]


class WkRefiner(Worker):
	name = "worker.refiner"

	refining_patterns = refining_patterns
	refining_regexes = refining_regexes

	tokenizer_pattern = re.compile(u"\W+")
	stemmer = WordNetLemmatizer()
	empty_string = re.compile("^\s*$")

	@staticmethod
	def filter_test(term):
		return not WkRefiner.empty_string.match(term)

	@staticmethod
	def clean_up(text):
		patterns  = WkRefiner.refining_patterns
		regexes = WkRefiner.refining_regexes
		for i in range(0, len(regexes)):
			r = regexes[i]
			_, replace = patterns[i]
			text = r.sub(replace, text)
		text = text.lower()
		return text

	@staticmethod
	def stem(token):
		return WkRefiner.stemmer.lemmatize(token)

	@staticmethod
	def tokenize(text):
		text = WkRefiner.clean_up(text)
		words = WkRefiner.tokenizer_pattern.split(text)
		return [WkRefiner.stemmer.lemmatize(w) for w in words if WkRefiner.filter_test(w)]