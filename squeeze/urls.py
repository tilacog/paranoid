from django.conf.urls import url

from squeeze import views


urlpatterns = [
    url(r'^$', views.landing, name='squeeze_page'),
    url(r'^receive$', views.receive_squeezejob, name='receive_squeezejob'),
]
