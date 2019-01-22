from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.machine_list, name='machine_list'),
]