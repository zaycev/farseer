# -*- coding: utf-8 -*-
import sys
import csv
import re

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine.url import URL
from options import DATABASE_CONFIG
from apps.nlp import WkRefiner

default_lexicon_file = "/Volumes/HFS/research/05.01.2012/lexicon-full.csv"
default_featureslist_file = "/Volumes/HFS/research/05.01.2012/features.csv"
default_stop_list_file = "/Volumes/HFS/research/05.01.2012/stoplist.csv"


def get_table_size(con, table, unique="id"):
	sql = "SELECT COUNT({0}) FROM {1};".format(unique, table)
	for count in connection.execute(sql):
		return count[0]


class Rule(object):
	def __init__(self):
		self.triggered = 0
	def apply(self, term, total_freq, doc_freq, rel_doc_freq):
		pass


class StopWordRule(Rule):
	def __init__(self, stoplist):
		super(StopWordRule, self).__init__()
		self.stoplist = stoplist
	def apply(self, term, total_freq, doc_freq, rel_doc_freq):
		if term in self.stoplist:
			self.triggered += 1
			return 1
		return 0

class MinFrequencyRule(Rule):
	def __init__(self, corpus_size):
		super(MinFrequencyRule, self).__init__()
		self.min_bound = corpus_size / 1000
	def apply(self, term, total_freq, doc_freq, rel_doc_freq):
		if doc_freq < self.min_bound:
			self.triggered += 1
			return 1
		return 0

class MaxFrequencyRule(Rule):
	def apply(self, term, total_freq, doc_freq, rel_doc_freq):
		if rel_doc_freq > 0.3:
			self.triggered += 1
			return 1
		return 0

class ContainsNumericRule(Rule):
	def __init__(self):
		super(ContainsNumericRule, self).__init__()
		self.regex = re.compile(".*[0-9]+.*")
	def apply(self, term, total_freq, doc_freq, rel_doc_freq):
		if self.regex.match(term):
			self.triggered += 1
			return 1
		return 0

class MinTermLengthRule(Rule):
	def apply(self, term, total_freq, doc_freq, rel_doc_freq):
		if len(term) <= 2:
			self.triggered += 1
			return 1
		return 0

class MaxTermLengthRule(Rule):
	def apply(self, term, total_freq, doc_freq, rel_doc_freq):
		if len(term) > 20:
			self.triggered += 1
			return 1
		return 0

def load_stoplist(stop_list_path, stemmer):
	csv.register_dialect("stoplist", delimiter=',', quotechar='"')
	stoplist = open(stop_list_path, "rb")
	stoplist_csv = csv.reader(stoplist, "stoplist")
	stoplist_set = set()
	for id, term in stoplist_csv:
		stoplist_set.add(stemmer.stem(term))
	stoplist.close()
	return stoplist_set

#
#
#
if len(sys.argv) < 2:
	print "\nError: Corpus table name is not specified. Exit.\n"
	exit(1)

corpus_table_name = sys.argv[1]
lexicon_file = sys.argv[2] if len(sys.argv) > 2  else default_lexicon_file
featureslist_file = default_featureslist_file

print "\nestablishing database connection"
url = URL(
	DATABASE_CONFIG["DB_DRIVER"],
	username=DATABASE_CONFIG["DB_USER"],
	password=DATABASE_CONFIG["DB_PASSWORD"],
	host=DATABASE_CONFIG["DB_HOST"],
	port=DATABASE_CONFIG["DB_PORT"],
	database=DATABASE_CONFIG["DB_DATABASE"]
)
db_engine = create_engine(url)
db_metadata = MetaData(bind=db_engine)
connection = db_engine.connect()

print "receiving corpus size"
corpus_sz = get_table_size(connection, corpus_table_name)
#corpus_sz = 12000
print "size in {0}".format(corpus_sz)
print "preparing for index corpus"
ref = WkRefiner()
lexicon_sz = 0
document_counter = 0
term_id = dict()
term_text = dict()
term_total_freq = []
term_doc_occurs = []
progress_indicators = 120
docs_progress_indicator = corpus_sz / progress_indicators
docs_progress = 0

print "start index documents\n"
sql = "SELECT post_title, post_short_text, full_text " \
	  "FROM {0} ORDER BY post_time DESC LIMIT {1};".format(corpus_table_name, corpus_sz)

docs = connection.execute(sql)

for i in xrange(0, progress_indicators / 2 - 3):
	sys.stdout.write("-")
sys.stdout.write("indexing")
for i in xrange(0, progress_indicators / 2 - 3):
	sys.stdout.write("-")

sys.stdout.write("\n[")
sys.stdout.flush()

for title, short, full in docs:
	indexed_terms = set()
	terms = ref.tokenize(title)\
		+ ref.tokenize(short)\
		+ ref.tokenize(full)
	for term in terms:
		if term not in term_id:
			tid = lexicon_sz
			term_text[tid] = term
			term_id[term] = tid
			lexicon_sz += 1
		else:
			tid = term_id[term]
		if len(term_total_freq) < lexicon_sz:
			term_total_freq.append(1)
			term_doc_occurs.append(1)
			indexed_terms.add(tid)
		else:
			term_total_freq[tid] += 1
			if tid not in indexed_terms:
				term_doc_occurs[tid] += 1
				indexed_terms.add(tid)
	document_counter += 1
	docs_progress += 1
	if docs_progress >= docs_progress_indicator:
		docs_progress = 0
		sys.stdout.write("#")
		sys.stdout.flush()
sys.stdout.write("]")
sys.stdout.flush()
connection.close()

print "\nindexing done !\n"

for i in xrange(0, progress_indicators / 2 - 2):
	sys.stdout.write("-")
sys.stdout.write("saving")
for i in xrange(0, progress_indicators / 2 - 2):
	sys.stdout.write("-")
sys.stdout.write("\n[")
sys.stdout.flush()


terms_progress_indicator = lexicon_sz / progress_indicators
terms_progress = 0
lexicon_fl = open(lexicon_file, "w")
columns = "tid,term,total_freq,doc_freq,rel_doc_freq\n"
csv_pattern = u"{0},\"{1}\",{2},{3},{4:0.16f}\n"
lexicon_fl.write(columns)
for i in xrange(0, lexicon_sz):
	tid = i
	term = term_text[tid]
	total_freq = term_total_freq[tid]
	doc_freq = term_doc_occurs[tid]
	rel_doc_freq = float(doc_freq) / float(corpus_sz)
	lexicon_fl.write(csv_pattern.format(
		tid, term, total_freq, doc_freq, rel_doc_freq).\
		encode("UTF-8"))
	terms_progress += 1
	if terms_progress >= terms_progress_indicator:
		terms_progress = 0
		sys.stdout.write("#")
		sys.stdout.flush()
sys.stdout.write("]\n")
sys.stdout.flush()

print "\nwrote {0} terms to {1}".format(lexicon_sz, lexicon_file)


print "\nstart filtering"
print "receiving stop list"
stoplist = load_stoplist(default_stop_list_file, ref)
print "stoplist contains {0} terms".format(len(stoplist))
print "generating rules"

rules = [
	StopWordRule(stoplist),
	MinFrequencyRule(corpus_sz),
	MaxFrequencyRule(),
	ContainsNumericRule(),
	MinTermLengthRule(),
	MaxTermLengthRule(),
]

print "generated {0} rules".format(len(rules))
print "start filtering"
for i in xrange(0, progress_indicators / 2 - 4):
	sys.stdout.write("-")
sys.stdout.write("filtering")
for i in xrange(0, progress_indicators / 2 - 3):
	sys.stdout.write("-")
sys.stdout.write("\n[")
sys.stdout.flush()

terms_progress_indicator = lexicon_sz / progress_indicators
terms_progress = 0
features_counter = 0
featurelist_fl = open(featureslist_file, "w")
columns = "tid,term,total_freq,doc_freq,rel_doc_freq\n"
csv_pattern = u"{0},\"{1}\",{2},{3},{4:0.16f}\n"
featurelist_fl.write(columns)
for i in xrange(0, lexicon_sz):
	tid = i
	term = term_text[tid]
	total_freq = term_total_freq[tid]
	doc_freq = term_doc_occurs[tid]
	rel_doc_freq = float(doc_freq) / float(corpus_sz)
	rules_test = [rule.apply(term, total_freq, doc_freq, rel_doc_freq) for rule in rules]
	if sum(rules_test) is 0:
		featurelist_fl.write(csv_pattern.format(
			tid, term, total_freq, doc_freq, rel_doc_freq).\
		encode("UTF-8"))

	terms_progress += 1
	if terms_progress >= terms_progress_indicator:
		terms_progress = 0
		sys.stdout.write("#")
		sys.stdout.flush()
sys.stdout.write("]\n")
sys.stdout.flush()

print
for rule in rules:
	print "rule {0} revomed {1} terms".format(rule.__class__.__name__, rule.triggered)




print "\ndone!\n"