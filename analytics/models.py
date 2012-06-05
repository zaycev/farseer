# -*- coding: utf-8 -*-

from django.db import models
from django.db import connection
from django.db.models import Min, Max
from collector.models import DataSet



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
	
	# name = models.CharField(max_length=128, null=False, blank=False)
	# key = models.CharField(max_length=16, null=False, blank=False,
	# 	db_index=True)
	# url = models.URLField(max_length=256, null=False, blank=False, unique=True,
	# 	verify_exists=False)
	# mime_type = models.CharField(max_length=32, null=False, blank=False,
	# 	default="text/html")
	# 
	# def __unicode__(self):
	# 	return u"<DocumentSource('#%s', '%s')>" % (self.id, self.name)