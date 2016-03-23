from django.conf.urls import url

from squeeze import views


urlpatterns = [
    url(r'^$', views.landing, name='squeeze_page'),
    url(r'^receive$', views.receive_squeezejob, name='receive_squeezejob'),
    url(r'^success/(\w+)/$', views.success_optin, name='success_optin'),
    url(r'^download/(\w+)/$', views.download_squeezejob, name='download_squeezejob'),
]
