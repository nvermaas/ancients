from django.urls import path

from . import views

app_name = "places"

urlpatterns = [
    path("", views.MapView.as_view(), name='index'),
    path("list", views.ListView.as_view(),name='list'),
    path("map", views.MapView.as_view(),name='map'),


    path('set_place_filter/<filter>', views.SetPlaceFilter, name='set-place-filter'),
]
