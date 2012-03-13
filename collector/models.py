# -*- coding: utf-8 -*-
from django.db import models


class Author(models.Model):
	name = models.CharField(max_length=128, null=False, blank=False)
	url = models.URLField(max_length=256, null=False, blank=False, unique=True, verify_exists=False)
	writer = models.BooleanField(default=False)

	def __unicode__(self):
		return u"<Author('#%s', '%s')>" % (self.id, self.name)


class DocumentSource(models.Model):
	name = models.CharField(max_length=128, null=False, blank=False)
	symbol = models.CharField(max_length=8, null=False, blank=False, db_index=True)
	url = models.URLField(max_length=256, null=False, blank=False, unique=True, verify_exists=False)

	def __unicode__(self):
		return u"<DocumentSource('#%s', '%s')>" % (self.id, self.name)


class River(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False, verify_exists=False)
	timestamp = models.DateTimeField(auto_created=True, null=False, blank=False)
	body = models.TextField(null=False, blank=False)
	source = models.ForeignKey(DocumentSource, rel_class=models.ManyToOneRel, null=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False)

	def __unicode__(self):
		return u"<River('#%s', '%s', '%s')>" % (self.id, self.url, self.timestamp)


class RawDocument(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False, unique=True, verify_exists=False)
	source = models.ForeignKey(DocumentSource, rel_class=models.ManyToOneRel, null=False)
	timestamp = models.DateTimeField(auto_created=True, null=False, blank=False)
	body = models.TextField(null=False, blank=False)
	river = models.ForeignKey(River, null=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False)

	def __unicode__(self):
		return u"<RawDocument('#%s', '%s', '%s')>" % (self.id, self.url, self.mime_type)


class Document(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False, unique=True, verify_exists=False)
	source = models.ForeignKey(DocumentSource, rel_class=models.ManyToOneRel, null=False)
	title = models.CharField(max_length=320, null=False, blank=False)
	summary = models.CharField(max_length=4096, null=False, blank=True)
	content = models.TextField(blank=False, null=False)
	image_url = models.URLField(max_length=256, null=True, blank=False, unique=False, verify_exists=False)
	published = models.DateTimeField(null=False, blank=False, db_index=True)
	authors = models.ManyToManyField(Author)
	mime_type = models.CharField(max_length=32, null=False, blank=False)

	def __unicode__(self):
		return u"<Document('#%s', '%s')>" % (self.id, self.title)


class ProbeSource(models.Model):
	name = models.CharField(max_length=128, null=False, blank=False)
	url = models.URLField(max_length=256, null=False, blank=False, unique=True, verify_exists=False)

	def __unicode__(self):
		return u"<ProbeSource('#%s', '%s')>" % (self.id, self.name)

class ProbeTag(models.Model):
	source = models.ForeignKey(ProbeSource, rel_class=models.ManyToOneRel, null=False)
	label = models.CharField(max_length=128, null=False, blank=False)
	symbol = models.CharField(max_length=8, null=False, blank=False, db_index=True)

	def __unicode__(self):
		return u"<ProbeTag('#%s', '%s', 'for %s')>" % (self.id, self.label, self.source.name)


class Probe(models.Model):
	signal = models.IntegerField(null=False, blank=False, db_index=True)
	document = models.ForeignKey(Document, rel_class=models.ManyToOneRel, null=False, db_index=True)
	tag = models.ForeignKey(ProbeTag, rel_class=models.ManyToOneRel, null=False, db_index=True)

	def __unicode__(self):
		return u"<Probe('#%s', 'from %s', '~ %s')>" % (self.id, self.tag.label, self.signal)


class RawProbe(models.Model):
	url = models.URLField(max_length=256, null=False, blank=False, unique=True, verify_exists=False)
	source = models.ForeignKey(ProbeSource, rel_class=models.ManyToOneRel, null=False)
	document = models.ForeignKey(Document, rel_class=models.ManyToOneRel, null=False)
	timestamp = models.DateTimeField(auto_created=True, null=False, blank=False)
	body = models.TextField(null=False, blank=False)
	mime_type = models.CharField(max_length=32, null=False, blank=False)

	def __unicode__(self):
		return u"<RawProbe('#%s', '%s', '%s')>" % (self.id, self.url, self.timestamp)