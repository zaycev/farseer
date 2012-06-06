# -*- coding: utf-8 -*-

from django.db import models
from collector.models import DataSet
from transformer.models import Token



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



class Term(models.Model):
	token = models.ForeignKey(Token, null=False, blank=False)
	sample = models.ForeignKey(Sample, null=False, blank=False)
	field = models.CharField(max_length=8, null=False, blank=False)
	freq = models.IntegerField(null=False, blank=False)

	class Meta:
		unique_together = ("token", "field", "sample")