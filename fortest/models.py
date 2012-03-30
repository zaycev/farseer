# -*- coding: utf-8 -*-

from django.db import models
import logging

class MockModel(models.Model):
	task = models.IntegerField()
	result = models.IntegerField()
	def save(self, force_insert=False, force_update=False, using=None):
		logging.debug("ok saved")