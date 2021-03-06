from django.conf.urls import *

urlpatterns = patterns('apps.userprofile.views',
    url(r'^$', 'my_profile', name='myprofile'),
    url(r'^update/$', 'update_profile', name='update_profile'),
    url(r'^history/$', 'history', name='user_history'),
    url(r'^inbox/$', 'user_inbox', name='inbox'),
    url(r'^alias/$', 'alias', name='alias'),
    url(r'^alias/add', 'add_alias', name='add_alias'),
    url(r'^alias/(?P<alias_id>\d+)/remove/$', 'remove_alias', name='remove_alias'),
    url(r'^(?P<username>[\w-]+)/$', 'user_profile', name='profile'),

)
