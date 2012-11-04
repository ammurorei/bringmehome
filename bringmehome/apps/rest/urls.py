from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^address/(?P<user_id>.+)/(?P<address_string>.+)/$', 'bringmehome.apps.rest.views.query_home_address', name='query_home_address'),
	url(r'^register/(?P<user_id>.+)/(?P<address_string>.+)/$', 'bringmehome.apps.rest.views.register_address', name='register_address'),
	url(r'^route/$', 'bringmehome.apps.rest.views.query_way_home', name='query_way_home'),
)