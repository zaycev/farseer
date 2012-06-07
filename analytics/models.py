# -*- coding: utf-8 -*-

import pickle
import numpy as np
from django.db import models
from collector.models import DataSet
from transformer.models import Token
from analytics.features import compute_vec
from django.db import connection

# from analytics.models import Sample
# s = Sample.objects.get(id=14907)
# s.to_feature_vector()
# list(s.keywords())

ICURSOR = connection.cursor()

class Sample(models.Model):
	id = models.IntegerField(primary_key=True)
	url = models.CharField(max_length=256, null=False, blank=False,
		db_index=True)
	title = models.CharField(max_length=192, null=False, blank=False)
	summary = models.CharField(max_length=8096, null=False, blank=False)
	content = models.TextField(null=False, blank=False)
	published = models.DateTimeField(null=False, blank=False, db_index=True)
	source_dataset = models.ForeignKey(DataSet, null=False, blank=False)
	year = models.IntegerField(null=False, db_index=True)
	month = models.IntegerField(null=False, db_index=True)
	day = models.IntegerField(null=False, db_index=True)
	dow = models.IntegerField(null=False, db_index=True)
	day_id = models.IntegerField(null=False, db_index=True)
	views = models.IntegerField(null=False, db_index=True)
	twits = models.IntegerField(null=False, db_index=True)
	comms = models.IntegerField(null=False, db_index=True)
	base_size = 18063
	fmap = None
	
	def keywords(self, tokens=None):
		if not tokens:
			tokens = {t.id:t for t in Token.objects.all()}
		tfidf = compute_vec(ICURSOR, self.id,
							Sample.objects.all().count(), tokens)
		tfidf.sort(key=lambda x: x[1])
		tfidf.reverse()
		for token_id, token_tfidf in tfidf:
			yield Token.objects.get(id=token_id).text, token_tfidf

	def to_feature_vector(self, tokens=None):
		if not tokens:
			tokens = {t.id:t for t in Token.objects.all()}
		
		tfidf = compute_vec(ICURSOR, self.id,
							Sample.objects.all().count(), tokens)
		
		
		features = np.zeros(5 + self.base_size, dtype=np.float32)
		for position, value in tfidf:
			features[position] = value
		features[self.base_size + 0] = self.year
		features[self.base_size + 1] = self.month
		features[self.base_size + 2] = self.day
		features[self.base_size + 3] = self.dow
		features[self.base_size + 4] = self.day_id
		
		if self.fmap:
			fmap = np.zeros(len(self.fmap), dtype=np.float32)
			for i in xrange(len(self.fmap)):
				fmap[i] = features[self.fmap[i]]
			return fmap
		else:
			return features
		
	def response(self):
		return np.array([self.views, self.twits,
						self.comms], dtype=np.float32)
	
	def class_label(self):
		if self.twits < 30:
			return 0
		elif self.twits >= 30 and self.twits < 100:
			return 1
		elif self.twits >= 100 and self.twits < 500:
			return 2
		return 3
		
	@staticmethod
	def set_fmap(fmap=None, fmap_file="fmap.pickle"):
		if not fmap:
			fmap = pickle.loads(open(fmap_file, "r").read())
		Sample.fmap = fmap



class Term(models.Model):
	token = models.ForeignKey(Token, null=False, blank=False)
	sample = models.ForeignKey(Sample, null=False, blank=False)
	field = models.CharField(max_length=8, null=False, blank=False)
	freq = models.IntegerField(null=False, blank=False)

	class Meta:
		unique_together = ("token", "field", "sample")