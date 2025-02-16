from .models import Place

from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, TemplateView
from places.services import algorithms



def redirect_with_params(view_name, params):
    return redirect(reverse(view_name) + params)


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

        # first check the dropdown button
        search = self.request.GET.get('place_type', None)
        if not search:
            # then check the search box
            search = self.request.GET.get('ancients_search_box', None)

        # convert the filtered places to leaflet features
        features = algorithms.create_features(search)

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

        # fill the type filter dropdown button (dropdown.html)
        types = Place.objects.values_list('type', flat=True).distinct()
        context['types'] = types

        return context


def SetPlaceFilter(request,filter):
    request.session['places_filter'] = filter
    return redirect('/ancients/?ancients_search_box=' + filter)

