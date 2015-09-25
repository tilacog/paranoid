from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'^login/$', 'accounts.views.login_page', name='login_page'),
    url(r'^login', 'accounts.views.login_view', name='login_view'),
)
