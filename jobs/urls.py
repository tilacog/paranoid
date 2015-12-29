from django.conf.urls import url

from jobs import views

urlpatterns = [
    url(r'^$', views.job_list, name='job_list'),
    url(r'^new/(\d+)/$', views.new_job, name='new_job'),
    url('^download/(\d+)/$', views.download_report, name='download_report'),

]
