# -*- coding: utf-8 -*-

import nltk.corpus
import nltk.tag
import itertools
from nltk.corpus import brown, conll2000, treebank
from nltk.tag import brill

def backoff_tagger(tagged_sents, tagger_classes, backoff=None):
	if not backoff:
		backoff = tagger_classes[0](tagged_sents)
		del tagger_classes[0]
	for cls in tagger_classes:
		tagger = cls(tagged_sents, backoff=backoff)
		backoff = tagger
	return backoff

def make_tagger():
	brown_reviews = brown.tagged_sents(categories=['reviews'])[1000:]
	brown_lore = brown.tagged_sents(categories=['lore'])[1000:]
	conll_train = conll2000.tagged_sents('train.txt')[2000:]
	treebank_train = treebank.tagged_sents()[2000:]
	train_sets = list(itertools.chain(
		brown_reviews,
		brown_lore,
		conll_train,
		treebank_train
	))
	tagger_classes = [
		nltk.tag.AffixTagger,
		nltk.tag.UnigramTagger,
		nltk.tag.BigramTagger,
		nltk.tag.TrigramTagger,
	]
	word_patterns = [
		(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),
		(r'.*ould$', 'MD'),
		(r'.*ing$', 'VBG'),
		(r'.*ed$', 'VBD'),
		(r'.*ness$', 'NN'),
		(r'.*ment$', 'NN'),
		(r'.*ful$', 'JJ'),
		(r'.*ious$', 'JJ'),
		(r'.*ble$', 'JJ'),
		(r'.*ic$', 'JJ'),
		(r'.*ive$', 'JJ'),
		(r'.*ic$', 'JJ'),
		(r'.*est$', 'JJ'),
		(r'^a$', 'PREP'),
	]
	raubt_tagger = backoff_tagger(
		train_sets,
		tagger_classes,
		backoff=nltk.tag.RegexpTagger(word_patterns),
	)
	templates = [
		brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,1)),
		brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (2,2)),
		brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,2)),
		brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,3)),
		brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,1)),
		brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (2,2)),
		brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,2)),
		brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,3)),
		brill.ProximateTokensTemplate(brill.ProximateTagsRule, (-1, -1), (1,1)),
		brill.ProximateTokensTemplate(brill.ProximateWordsRule, (-1, -1), (1,1)),
	]
	trainer = brill.FastBrillTaggerTrainer(raubt_tagger, templates)
	braubt_tagger = trainer.train(train_sets, max_rules=100, min_score=3)
	return braubt_tagger