from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    #outside landing page
    url(r'^$', 'bringmehome.apps.web.views.landing', name='landing'),

    #new user auth landing page
    url(r'^signup/(?P<user_id>.+)/$', 'bringmehome.apps.web.views.home', name='home'),
    url(r'^privacy$', 'bringmehome.apps.web.views.privacy', name='privacy'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^oauth/', include('bringmehome.apps.oauth.urls')),
    (r'^rest/', include('bringmehome.apps.rest.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
