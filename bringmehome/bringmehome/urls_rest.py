from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^address/(?P<address_string>.+)/$', 'bringmehome.views_rest.query_home_address', name='query_home_address'),
	url(r'^route/(?P<location>.+)/(?P<address_string>.+)/$', 'bringmehome.views_rest.query_way_home', name='query_way_home'),
)