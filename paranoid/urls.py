from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    # url(r'^$', 'paranoid.views.home', name='home'),
    url(r'^$', 'audits.views.home_page', name='home_page'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^audits/', include('audits.urls')),
    url(r'^jobs/', include('jobs.urls')),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
)
