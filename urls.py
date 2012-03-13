from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from web.views import index, result

admin.autodiscover()
urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', index),
	url(r'^index/$', index),
	url(r'^result/$', result),
)
