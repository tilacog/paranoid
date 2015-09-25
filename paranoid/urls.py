from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    # url(r'^$', 'paranoid.views.home', name='home'),
    url(r'^$', 'audits.views.home_page', name='home_page'),
    url(r'^audits/', include('audits.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^jobs/(\d+)/$', 'jobs.views.new_job', name='new_job'),
)
