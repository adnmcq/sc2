from django.conf.urls import url

from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^food_select_options/$', views.food_select_options, name='food_select_options'),
    url(r'^unit_select_options/$', views.unit_select_options, name='unit_select_options'),
]