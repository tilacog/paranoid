from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/$', 'audits.views.audit_page', name='audit_page'),
)
