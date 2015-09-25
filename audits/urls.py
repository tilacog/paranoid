from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'^(\d+)/$', 'audits.views.audit_page', name='audit_page'),
)
