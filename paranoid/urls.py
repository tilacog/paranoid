from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # url(r'^$', 'paranoid.views.home', name='home'),
    url(r'^$', 'audits.views.home_page', name='home_page'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^/login/$', 'accounts.views.login_page', name='login_page'),
    url(r'^/login', 'accounts.views.login_view', name='login_view'),
)
