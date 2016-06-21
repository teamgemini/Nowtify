from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
                       url(r'^$', views.login, name='login'),
                       url(r'^index/', views.index, name='index'),
                       url(r'^charts/', views.index, name='charts'),
                       url(r'^forms/', views.index, name='forms'),
                       url(r'^icons/', views.index, name='icons'),
                       url(r'^panels/', views.index, name='panels'),
                       url(r'^tables/', views.index, name='tables'),
                       url(r'^widgets/', views.index, name='widgets')

                       # Nowtify Pages
                       # url(r'^overview/', views.index, name='overview'),
                       # url(r'^/user', views.user, name='user'),
                       # url(r'^sensor/', views.sensor, name='sensor'),
                       # url(r'^wearable/', views.wearable, name='wearable'),
                       # url(r'^dashboard/', views.dashboard, name='dashboard')

                       )

