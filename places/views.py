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

        # first check the dropdown buttons
        # when they are changed, put the new value on the session... otherwise read the old value from the session
        country = self.request.GET.get('country', "netherlands")
        if country:
            self.request.session['country'] = country
        else:
            try:
                country = self.request.session['country']
            except:
                country = "netherlands"
                self.request.session['country'] = country

        place_type = self.request.GET.get('place_type', "Stone Circle")
        if place_type:
            self.request.session['place_type'] = place_type
        else:
            try:
                place_type = self.request.session['place_type']
            except:
                place_typetry = "Stone Circle"
                self.request.session['place_type'] = place_type

        search = self.request.GET.get('ancients_search_box', None)
        if not search:
            search = place_type

        #country = self.request.session['country_filter']
        # convert the filtered places to leaflet features
        features = algorithms.create_features(country, search)

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
        countries = Place.objects.values_list('country', flat=True).distinct()
        context['countries'] = countries
        context['country'] = country

        #types = Place.objects.filter(country=country).values_list('type', flat=True).distinct()
        types = Place.objects.values_list('type', flat=True).distinct()
        context['types'] = types
        context['place_type'] = place_type

        return context


# def SetPlaceFilter(request,filter):
#     request.session['places_filter'] = filter
#     return redirect('/ancients/?ancients_search_box=' + filter)
#
# def SetCountryFilter(request,filter):
#     request.session['country_filter'] = filter
#     return redirect('/ancients/?ancients_search_box=' + filter)
