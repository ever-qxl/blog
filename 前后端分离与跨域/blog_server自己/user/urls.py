from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.users, name='users'),
    url(r'^/(?P<username>[\w]{1,11})$',
        views.users, name='user'),
    url(r'^/(?P<username>[\w]{1,11})/avatar$',
        views.user_avatar, name='user_avatar'),
]
