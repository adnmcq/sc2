from django.conf.urls import url

from app import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^recipe/$', views.recipe, name='recipe'),
    url(r'^recipe/(?P<id>[0-9]+)/$', views.recipe, name='recipe'),
    url(r'^food_select_options/$', views.food_select_options, name='food_select_options'),
    url(r'^unit_select_options/$', views.unit_select_options, name='unit_select_options'),
]