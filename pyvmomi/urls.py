from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.machine_list, name='machine_list'),
    url(r'^machine/(?P<pk>\d+)/$', views.machine_detail, name='machine_detail'),
    url('pyvmomi/machine_list.html', views.machine_list),
]