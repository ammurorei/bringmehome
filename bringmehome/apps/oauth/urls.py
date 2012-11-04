from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^callback/?$', 'bringmehome.apps.oauth.views.callback', name='callback'),

)