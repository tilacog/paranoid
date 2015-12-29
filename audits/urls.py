from django.conf.urls import url

from audits import views


urlpatterns = [
    url(r'^(\d+)/$', views.audit_page, name='audit_page'),
]
