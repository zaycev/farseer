# -*- coding: utf-8 -*-

from django.db import models
from collector.models import DataSet



class Lexicon(models.Model):
	dataset = models.ForeignKey(DataSet)
	name = models.CharField(max_length=64, null=False, blank=False)
	doc_size = models.IntegerField(null=False, blank=False)
	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False,
		db_index=True)

	

class Token(models.Model):
	lexicon = models.ForeignKey(Lexicon, null=False, blank=False)
	postag = models.CharField(max_length=64, null=True, blank=True,
		db_index=True)
	nertag = models.CharField(max_length=64, null=True, blank=True,
		db_index=True)
	text = models.CharField(max_length=256, null=False, blank=False,
		db_index=True)
	origin = models.CharField(max_length=256, null=True, blank=True,
		db_index=True)
	tfreq = models.IntegerField(null=False, blank=False, db_index=True)
	dfreq = models.IntegerField(null=False, blank=False, db_index=True)
	rfreq = models.FloatField(null=False, blank=False, db_index=True)

	def __unicode__(self):
		return u"<Token(id=#%s, '%s', '%s', '%s')>"\
			% (self.id, self.text, self.postag, self.nertag)



class StopWord(models.Model):
	language = models.CharField(max_length=3, null=False, blank=False,
		db_index=True)
	text = models.CharField(max_length=256, null=False, blank=False,
		db_index=True)