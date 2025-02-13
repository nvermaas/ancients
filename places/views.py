from .models import Place

from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, TemplateView

from places.services import algorithms

def redirect_with_params(view_name, params):
    return redirect(reverse(view_name) + params)

class IndexView(TemplateView):
    model = Place
    template_name = "index.html"
    queryset = Place.objects.all()

    def get_context_data(self, **kwargs):

        context = (
            super().get_context_data(
                **kwargs
            )
        )

        # get the period-to-check from the session
        try:
            type = self.request.session['type']
        except:
            self.request.session['type'] = "all"

        # convert them to leaflet features
        features = algorithms.create_features()
        if not features:
            features = []

        context["markers"] = {
          "type": "FeatureCollection",
          "crs": {
            "type": "name",
            "properties": {
              "name": "EPSG:4326"
            }
          },
          "features": features
        }

        context["type"] = self.request.session['type']

        return context

class ListView(ListView):
    model = Place
    queryset = Place.objects.all()
    template_name = "list.html"

class MapView(ListView):
    model = Place
    queryset = Place.objects.all()
    template_name = "map.html"

    def get_context_data(self, **kwargs):

        context = (
            super().get_context_data(
                **kwargs
            )
        )

        # convert them to leaflet features
        features = algorithms.create_features()
        if not features:
            features = []

        context["markers"] = {
          "type": "FeatureCollection",
          "crs": {
            "type": "name",
            "properties": {
              "name": "EPSG:4326"
            }
          },
          "features": features
        }

        return context



