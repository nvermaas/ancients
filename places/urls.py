from django.urls import path

from . import views

app_name = "places"

urlpatterns = [
    path("list", views.ListView.as_view(),name='list'),
    path("map", views.MapView.as_view(),name='map'),
    path("", views.MapView.as_view(),name='index'),
]
