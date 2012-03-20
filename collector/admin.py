# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
import collector.models as collector

class DocumentSourceAdmin(admin.ModelAdmin):
	list_display = ("name", "symbol", "url", "id",)
	list_filter = ("name", "symbol",)

class RawRiverAdmin(admin.ModelAdmin):
	list_display = ("url", "timestamp", "source", "mime_type",)
	list_filter = ("source", "timestamp",)

#class SearchEntryFrom(forms.ModelForm):
#	search_body = forms.CharField(widget=forms.Textarea, required=True, label=u"Search Body")
#	type = forms.TypedChoiceField(choices=SEARCH_CLASSES_CHOICES, widget=forms.RadioSelect, label=u"Content Type")
#	class Meta:
#		model = SearchEntry


admin.site.register(collector.DocumentSource, DocumentSourceAdmin)
admin.site.register(collector.RawRiver, RawRiverAdmin)