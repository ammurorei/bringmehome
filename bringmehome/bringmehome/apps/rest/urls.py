from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^address/(?P<address_string>.+)/$', 'bringmehome.apps.rest.views.query_home_address', name='query_home_address'),
	url(r'^route/$', 'bringmehome.apps.rest.views.query_way_home', name='query_way_home'),
)