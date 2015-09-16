from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # url(r'^$', 'paranoid.views.home', name='home'),
    url(r'^$', 'audits.views.home_page', name='home_page'),
    url(r'^audits/', include('audits.urls')), 
    url(r'^accounts/', include('accounts.urls')),
)
