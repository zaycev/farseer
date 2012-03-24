from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

import web.views as web
import collector.views as collector

admin.autodiscover()
urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', web.index),

	url(r'^apps/collector/$', collector.apps),
	url(r'^apps/collector/service/([a-zA-Z0-9]+)$', collector.show_service),
	url(r'^apps/collector/dataset/([a-zA-Z0-9]+)$', collector.show_dataset),
	url(r'^apps/collector/api/v0/call/$', collector.call),
)