from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout

import audits

urlpatterns = [
    url(r'^$', audits.views.home_page, name='home_page'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^audits/', include('audits.urls')),
    url(r'^jobs/', include('jobs.urls')),
    url(r'^logout$', logout, {'next_page': '/'}, name='logout'),
]
