from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

import web.views as web
import collector.views as collector

admin.autodiscover()
urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', web.index),
	url(r'^apps/collector/$', collector.list_apps),
)