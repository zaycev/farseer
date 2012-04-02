# -*- coding: utf-8 -*-

from django.db import models
from django.db import connection
from django.db.models import Min, Max

import datetime

class DocumentSource(models.Model):
	name = models.CharField(max_length=128, null=False, blank=False)
	key = models.CharField(max_length=16, null=False, blank=False,
		db_index=True)
	url = models.URLField(max_length=256, null=False, blank=False, unique=True,
		verify_exists=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False,
		default="text/html")

	def __unicode__(self):
		return u"<DocumentSource('#%s', '%s')>" % (self.id, self.name)


class DataSet(models.Model):
	name = models.CharField(max_length=48, null=False, blank=False,
		db_index=True, unique=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False,
		db_index=True)
	summory = models.CharField(max_length=4096, null=True, blank=True)

#	def save(self, *args, **kwargs):
#		if not self.id:
#			self.timestamp = datetime.datetime.now()

	def __unicode__(self):
		return u"<Dataset('#%s', '%s')>" % (self.id, self.name)

	@property
	def river_mime_types(self):
		for m in self.rawriver_set.values("mime_type").distinct():
			m["count"] = RawRiver.objects\
						.filter(dataset=self, mime_type=m["mime_type"]).count()
			yield m

	@property
	def river_sources(self):
		sources = RawRiver.objects.filter(dataset=self)\
			.values("source").distinct()
		for s in sources:
			yield DocumentSource.objects.get(id=s["source"])

	@property
	def random_river(self):
		return self.rawriver_set.order_by("?").values("id")[0]


	@property
	def rawdoc_percentage(self):
		urlsc = self.extractedurl_set.count()
		if urlsc:
			return float(self.rawdocument_set.count())\
					/ urlsc * 100
		return "?"


	@property
	def rawdoc_mime_types(self):
		for m in self.rawdocument_set.values("mime_type").distinct():
			m["count"] = RawRiver.objects\
			.filter(dataset=self, mime_type=m["mime_type"]).count()
			yield m

	@property
	def collecting_period(self):
		_min, _max = Min("timestamp"), Max("timestamp")
		min_date = RawRiver.objects.filter(dataset=self).aggregate(_min)
		max_date = RawRiver.objects.filter(dataset=self).aggregate(_max)
		return {
			"since": min_date["timestamp__min"],
			"to": max_date["timestamp__max"],
		}


	def unfetched_rawdocs(self, input_dataset):
		return ExtractedUrl.objects.extra(
			where=["dataset_id=%s AND url NOT IN "
				   "(SELECT url FROM collector_rawdocument "
				   "WHERE dataset_id=%s)"],
			params=[input_dataset.id, self.id],
		)

	def rawdocs(self, input_dataset):
		return RawDocument.objects.extra(
			where=["dataset_id=%s AND url NOT IN "
				   "(SELECT url FROM collector_document "
				   "WHERE dataset_id=%s)"],
			params=[input_dataset.id, self.id],
		)
		
	def docs_by_year(self):
		sql = """SELECT year, (SELECT count(*)::int4
					FROM collector_document
					WHERE dataset_id=%s
						AND EXTRACT(YEAR from published)=year)
		FROM
			(SELECT DISTINCT EXTRACT(YEAR from t1.published)::int2 as year
			FROM collector_document as t1
			WHERE dataset_id=%s) AS t_years
		ORDER BY year ASC;
		"""
		cursor = connection.cursor()
		cursor.execute(sql, (self.id, self.id,))
		rows = cursor.fetchall()
		cursor.close()
		return rows

	class Meta:
		ordering = ("name",)


class RawRiver(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False,
		verify_exists=False)
	source = models.ForeignKey(DocumentSource, rel_class=models.ManyToOneRel,
		null=False)
	dataset = models.ForeignKey(DataSet, rel_class=models.ManyToOneRel,
		null=False, db_index=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False,
		db_index=True)
	body = models.TextField(null=False, blank=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False)

#	def save(self, *args, **kwargs):
#		if not self.id:
#			self.timestamp = datetime.datetime.now()

	def __unicode__(self):
		return u"<RawRiver('#%s', '%s', '%s')>" % (self.id, self.url,
												   self.timestamp)


class ExtractedUrl(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False,
		verify_exists=False, db_index=True)
	dataset = models.ForeignKey(DataSet, rel_class=models.ManyToOneRel,
		null=False, db_index=True)
	source = models.ForeignKey(DocumentSource, rel_class=models.ManyToOneRel,
		null=False)

	def __unicode__(self):
		return u"<ExtractedUrl(id='%s', url='%s', dataset='%s')>" \
				% (self.id, self.url, self.dataset.id)

	class Meta:
		unique_together = ("url", "dataset",)


class RawDocument(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False,
		verify_exists=False, db_index=True)
	dataset = models.ForeignKey(DataSet, rel_class=models.ManyToOneRel,
		null=False, db_index=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False,
		db_index=True)
	body = models.TextField(null=False, blank=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False,
		default="text/html")

#	def save(self, *args, **kwargs):
#		if not self.id:
#			self.timestamp = datetime.datetime.now()

	def __unicode__(self):
		return u"<RawDocument('#%s', '%s', '%s')>" % (self.id, self.url,
													  self.mime_type)

	class Meta:
		unique_together = ("url", "dataset",)


class Document(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False,
		verify_exists=False, db_index=True)
	dataset = models.ForeignKey(DataSet, rel_class=models.ManyToOneRel,
		null=False, db_index=True)
	title = models.CharField(max_length=320, null=False, blank=False)
	summary = models.CharField(max_length=4096, null=False, blank=True)
	content = models.TextField(blank=False, null=False)
	image_url = models.URLField(max_length=256, null=True, blank=False,
		unique=False, verify_exists=False)
	published = models.DateTimeField(null=False, blank=False, db_index=True)
	mime_type = models.CharField(default="text", max_length=32, null=False,
		blank=False)
	
	def __unicode__(self):
		return u"<Document(id=%s, dataset=%s, title='%s')>"\
			% (self.id, self.dataset.id, self.title)

	class Meta:
		unique_together = ("url", "dataset",)


class Author(models.Model):
	url = models.URLField(primary_key=True, max_length=256, null=False,
		blank=False, unique=True, verify_exists=False, db_index=True)
	name = models.CharField(max_length=128, null=True, blank=True)
	documents = models.ManyToManyField(Document)

	def __unicode__(self):
		return u"<Author(id=#%s, name='%s')>" % (self.id, self.name)


#class ProbeSource(models.Model):
#	name = models.CharField(max_length=128, null=False, blank=False)
#	symbol = models.CharField(max_length=16, null=False, blank=False,
#		db_index=True)
#	url = models.URLField(max_length=256, null=False, blank=False, unique=True,
#		verify_exists=False)
#
#	def __unicode__(self):
#		return u"<ProbeSource('#%s', '%s')>" % (self.id, self.name)
#
#
#class ProbeTag(models.Model):
#	source = models.ForeignKey(ProbeSource, rel_class=models.ManyToOneRel,
#		null=False)
#	symbol = models.CharField(max_length=16, null=False, blank=False,
#		db_index=True)
#	label = models.CharField(max_length=128, null=False, blank=False)
#
#	def __unicode__(self):
#		return u"<ProbeTag('#%s', '%s', 'for %s')>" % (self.id, self.label,
#													   self.source.name)
#
#
#class Probe(models.Model):
#	signal = models.IntegerField(null=False, blank=False, db_index=True)
#	document = models.ForeignKey(Document, rel_class=models.ManyToOneRel,
#		null=False, db_index=True)
#	tag = models.ForeignKey(ProbeTag, rel_class=models.ManyToOneRel, null=False,
#		db_index=True)
#
#	def __unicode__(self):
#		return u"<Probe('#%s', 'from %s', '~ %s')>" % (self.id, self.tag.label,
#													   self.signal)
#
#
#class RawProbe(models.Model):
#	url = models.URLField(max_length=256, null=False, blank=False, unique=True,
#		verify_exists=False)
#	source = models.ForeignKey(ProbeSource, rel_class=models.ManyToOneRel,
#		null=False)
#	document = models.ForeignKey(Document, rel_class=models.ManyToOneRel,
#		null=False)
#	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)
#	body = models.TextField(null=False, blank=False)
#	mime_type = models.CharField(max_length=32, null=False, blank=False)
#
#	def __unicode__(self):
#		return u"<RawProbe('#%s', '%s', '%s')>" % (self.id, self.url,
#												   self.timestamp)