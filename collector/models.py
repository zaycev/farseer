# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Min, Max


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
	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	summory = models.CharField(max_length=4096, null=True, blank=True)
	sources = models.ManyToManyField(DocumentSource)

	def __unicode__(self):
		return u"<Dataset('#%s', '%s')>" % (self.id, self.name)

	@property
	def mime_types(self):
		for m in self.rawriver_set.values("mime_type").distinct():
			m["count"] = RawRiver.objects\
						.filter(mime_type=m["mime_type"]).count()
			yield m

	@property
	def counted_sources(self):
		for source in self.sources.all():
			yield {
				"source": source,
				"rawrivers": RawRiver.objects\
							.filter(dataset=self, source=source).count(),
			}

	@property
	def collecting_period(self):
		min_date = RawRiver.objects.filter(dataset=self).aggregate(Min("timestamp"))
		max_date = RawRiver.objects.filter(dataset=self).aggregate(Max("timestamp"))
		return {
			"since": min_date["timestamp__min"],
			"to": max_date["timestamp__max"],
		}

	class Meta:
		ordering = ("name",)


class RawRiver(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False,
		verify_exists=False)
	source = models.ForeignKey(DocumentSource, rel_class=models.ManyToOneRel,
		null=False)
	dataset = models.ForeignKey(DataSet, rel_class=models.ManyToOneRel,
		null=False, db_index=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	body = models.TextField(null=False, blank=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False)

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
		return u"<ExtractedUrl('#%s', '%s')>" % (self.id, self.url)

	class Meta:
		unique_together = ("url", "dataset",)

class RawDocument(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False,
		verify_exists=False, db_index=True)
	dataset = models.ForeignKey(DataSet, rel_class=models.ManyToOneRel,
		null=False, db_index=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	body = models.TextField(null=False, blank=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False,
		default="text/html")

	def __unicode__(self):
		return u"<RawDocument('#%s', '%s', '%s')>" % (self.id, self.url,
													  self.mime_type)

	class Meta:
		unique_together = ("url", "dataset",)

		#class Author(models.Model):
#	name = models.CharField(max_length=128, null=False, blank=False)
#	url = models.URLField(max_length=256, null=False, blank=False, unique=True,
#		verify_exists=False, db_index=True)
#
#	def __unicode__(self):
#		return u"<Author('#%s', '%s')>" % (self.id, self.name)
#
#
#class Document(models.Model):
#	url = models.ForeignKey(ExtractedUrl, to_field="url", max_length=256,
#		db_index=True, null=False, blank=False)
#	source = models.ForeignKey(DocumentSource, rel_class=models.ManyToOneRel,
#		null=False)
#	title = models.CharField(max_length=320, null=False, blank=False)
#	summary = models.CharField(max_length=4096, null=False, blank=True)
#	content = models.TextField(blank=False, null=False)
#	image_url = models.URLField(max_length=256, null=True, blank=False,
#		unique=False, verify_exists=False)
#	published = models.DateTimeField(null=False, blank=False, db_index=True)
#	authors = models.ManyToManyField(Author)
#	mime_type = models.CharField(max_length=32, null=False, blank=False)
#
#	def __unicode__(self):
#		return u"<Document('#%s', '%s')>" % (self.id, self.title)
#
#
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