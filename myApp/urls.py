from django.urls import re_path, path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.empty_view, name='empty'),

    re_path(r'^login/$', views.login_view, name='login'),

    re_path(r'^logout/$', views.logout_view, name='logout'),

    re_path(r'^profile/$', views.get_profile, name='get_profile'),
]