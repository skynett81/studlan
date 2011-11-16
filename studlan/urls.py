from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'studlan.news.views.main', name='news'),
    url(r'^login.html', 'studlan.competition.views.log_in'),
    url(r'^logout.html', 'studlan.competition.views.log_out'),
    url(r'^register.html', 'studlan.competition.views.register_user'),
    url(r'^competitions/', include('studlan.competition.urls')),
    url(r'^misc/remove_alert.html', 'studlan.misc.views.remove_alert'),
    url(r'^teams/', 'studlan.competition.views.teams', name='teams'),
    # Examples:
    # url(r'^$', 'studlan.views.home', name='home'),
    # url(r'^studlan/', include('studlan.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
