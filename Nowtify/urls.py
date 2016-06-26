from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^', include('NowtifyWeb.urls'))
    # url(r'^admin/', include(admin.site.urls)),
)