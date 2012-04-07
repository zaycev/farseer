# -*- coding: utf-8 -*-

from django.db import models

import re


class SDocument(models.Model):
	db_table = "search_sdocument"
	url = models.URLField(max_length=256, null=False, blank=False,
		verify_exists=False, db_index=True)
	title = models.CharField(max_length=320, null=False, blank=False)
	content = models.TextField(blank=False, null=False)
	published = models.DateTimeField(null=False, blank=False, db_index=True)
	vi = models.IntegerField(null=False, blank=False)
	co = models.IntegerField(null=False, blank=False)

	re_empty = re.compile("\s+")
	@staticmethod
	def search_ids(query):
		return SDocument.objects.extra(
			where=["fts @@ plainto_tsquery('english',%s)"],
			params=[query],
		).order_by("-vi").values("id")

	
	@staticmethod
	def search(query):
		return SDocument.objects.extra(
			where=["fts @@ plainto_tsquery('english',%s)"],
			params=[query],
		).order_by("-vi")

	@staticmethod
	def search_popular(q1, q2):
		q1 = q1.visible_text if isinstance(q1, SToken) else q1
		q2 = q2.visible_text if isinstance(q2, SToken) else q2
		return SDocument.objects.extra(
			where=["fts @@ to_tsquery('english',%s)"],
			params=[re.sub(SDocument.re_empty, "|", "(%s)&(%s)" % (q1, q2))],
		).order_by("-vi").values("id","url","title","vi")[0:8]

class SToken(models.Model):
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

	@property
	def visible_text(self):
		if self.origin:
			return self.origin
		return self.text

	def related(self):
		return SToken.search(self.visible_text).exclude(id=self.id)[0:16]

	re_empty = re.compile("\s+")
	@staticmethod
	def search(query):
		query = re.sub(SToken.re_empty, "|", query)
		return SToken.objects.extra(
			select = {
				"rank": "ts_rank_cd(fts, to_tsquery('english',%s), 32)",
			},
			where=["fts @@ to_tsquery('english',%s)"],
			params=[query],
			select_params=[query]
		).order_by("-rank")

	def __unicode__(self):
		return u"<SToken(id=#%s, '%s')>"\
			% (self.id, self.origin if self.origin else self.text)


