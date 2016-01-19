from django.conf.urls import url

from squeeze import views


urlpatterns = [
    url(r'^$', views.landing, name='squeeze_page'),
]
