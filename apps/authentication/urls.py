# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.authentication.views',
        url(r'^login/$', 'login', name='auth_login'),
        url(r'^logout/$', 'logout', name='auth_logout'),
        url(r'^register/$', 'register', name='auth_register'),
        url(r'^direct_register/$', 'direct_register', name='auth_direct_register'),
        url(r'^verify/(\w+)/$', 'verify'),
        url(r'^recover/$', 'recover', name='auth_recover'),
        url(r'^set_password/(\w+)/$', 'set_password', name='auth_set_password'),
)
