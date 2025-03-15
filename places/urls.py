from django.urls import path

from . import views

app_name = "places"

urlpatterns = [
    path("", views.MapView.as_view(), name='index'),
    path("list", views.ListView.as_view(),name='list'),
    path("map", views.MapView.as_view(),name='map'),
    path("welcome", views.welcome, name='welcome'),
    path("reload_data", views.reload_data,name='reload-data'),
    path("set_view/<place_id>", views.set_view, name='set-view'),
    path("set_google_maps/<place_id>", views.set_google_maps, name='set-google-maps'),
    #path('set_place_filter/<filter>', views.SetPlaceFilter, name='set-place-filter'),
    #path('set_country_filter/<filter>', views.SetCountryFilter, name='set-country-filter'),
]
