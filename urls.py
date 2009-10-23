from django.conf.urls.defaults import *
from invoicemaster.settings import MEDIA_ROOT

urlpatterns = patterns('',
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^accounts/', include('registration.urls')),
    (r'^$', "django.contrib.auth.views.login"),
 )

urlpatterns += patterns('django.views.generic.simple',
)
