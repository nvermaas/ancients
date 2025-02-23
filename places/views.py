from .models import Place

from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from places.services import algorithms
from django.contrib.auth.decorators import login_required

class ListView(ListView):
    model = Place
    #queryset = Place.objects.all()
    template_name = "list.html"

    def get_queryset(self):
        country, place_type, search = algorithms.get_current_filter_values(self.request)
        return algorithms.select_records(country,place_type)

    def get_context_data(self, **kwargs):

        context = (
            super().get_context_data(
                **kwargs
            )
        )

        country,place_type,search = algorithms.get_current_filter_values(self.request)
        places = algorithms.select_records(country,place_type)
        context['places'] = places

        # fill the type filter dropdown button (dropdown.html)
        countries = Place.objects.values_list('country', flat=True).distinct()
        context['countries'] = countries
        context['country'] = country

        if country == 'All':
            types = Place.objects.values_list('type', flat=True).distinct()
        else:
            # only load the types that are valid for this country
            types = Place.objects.filter(country=country).values_list('type', flat=True).distinct()

        if len(types) == 1:
            # only 1 type, so select it
            place_type = str(types[0])
            self.request.session['place_type'] = place_type

        context['types'] = types
        context['place_type'] = place_type

        return context

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

        country,place_type,search = algorithms.get_current_filter_values(self.request)
        places = algorithms.select_records(country,place_type)


        features = algorithms.create_features(places)

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

        if country == 'All':
            types = Place.objects.values_list('type', flat=True).distinct()
        else:
            # only load the types that are valid for this country
            types = Place.objects.filter(country=country).values_list('type', flat=True).distinct()

        if len(types) == 1:
            # only 1 type, so select it
            place_type = str(types[0])
            self.request.session['place_type'] = place_type

        context['types'] = types
        context['place_type'] = place_type

        return context

def welcome(request):
    """
    welcome page
    """
    return render(request,'welcome.html')

@login_required
def reload_data(request):
    """
    recreate the database by reloading all the kml files from the data directory
    """
    algorithms.reload_data()
    return redirect('/ancients')