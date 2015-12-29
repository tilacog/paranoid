from django.conf.urls import url

from accounts import views

urlpatterns = [
    url(r'^login/$', views.login_page, name='login_page'),
    url(r'^login', views.login_view, name='login_view'),
]
