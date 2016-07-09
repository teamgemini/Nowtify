from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
                       url(r'^$', views.custom_login, name='custom_login'),
                       url(r'^login/', views.login, name='login'),
                       url(r'^authentication/', views.authentication, name='authentication'),
                       url(r'^change-password/', views.change_password, name='change_password'),
                       url(r'^index/', views.index, name='index'),
                       url(r'^overview/', views.overview, name='overview'),
                       url(r'^sensor/', views.sensor, name='sensor'),
                       url(r'^logout/', views.logout, name='logout'),
                       url(r'^wearable/', views.wearable, name='wearable'),
                       url(r'^dashboard/', views.dashboard, name='dashboard'),
                       url(r'^wearable/', views.wearable, name='wearable'),
                       url(r'^dashboard/', views.dashboard, name='dashboard'),
                       url(r'^change_password/', views.settings, name='settings'),
                       url(r'^alert/', views.alert, name='alert')


# Nowtify Pages
                       # url(r'^overview/', views.index, name='overview'),
                       # url(r'^/user', views.user, name='user'),
                       # url(r'^sensor/', views.sensor, name='sensor'),
                       # url(r'^wearable/', views.wearable, name='wearable'),
                       # url(r'^dashboard/', views.dashboard, name='dashboard')

                       )
