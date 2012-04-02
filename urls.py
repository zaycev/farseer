from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

import collector.views as collector
import analyzer.views as analyzer

admin.autodiscover()
urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),

	url(r'^apps/collector/$', collector.apps),
	url(r'^apps/collector/service/([a-zA-Z0-9]+)$', collector.show_service),
	url(r'^apps/collector/dataset/([a-zA-Z0-9]+)$', collector.show_dataset),

	url(r'^apps/collector/api/v0/service/call\.(json|xml)$', collector.service_call),

	url(r'^apps/collector/api/v0/model/get\.(json|xml)$', collector.model_get),
	url(r'^apps/collector/api/v0/model/list\.(json|xml)$', collector.model_list),
	url(r'^apps/collector/api/v0/model/delete\.(json|xml)$', collector.service_call),
	
	url(r'^apps/analyzer/api/v0/model/get\.(json|xml|html)$', analyzer.model_get),
)

urlpatterns += patterns('', (
	r'^www/(?P<path>.*)$',
	'django.views.static.serve',
		{'document_root': 'www'}
))