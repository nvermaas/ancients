from django.urls import path

from . import views

app_name = "places"

urlpatterns = [
    path("list", views.ListView.as_view()),
    path("map", views.MapView.as_view()),
    path("", views.IndexView.as_view()),
]
