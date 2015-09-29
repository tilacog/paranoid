from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'jobs.views.job_list', name='job_list'),
    url(r'^new/(\d+)/$', 'jobs.views.new_job', name='new_job'),
    url('^download/(\d+)/$', 'jobs.views.download_report', name='download_report'),

)
