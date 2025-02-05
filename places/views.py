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

        # geolocate the ips
        places = Place.objects.all()

        # convert them to leaflet features
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

        context["type"] = self.request.session['type']

        return context

class MarkersMapView(TemplateView):
    template_name = "map.html"

    def get_context_data(self, **kwargs):

        context = (
            super().get_context_data(
                **kwargs
            )
        )

        # retrieve the IP from the url parameters
        ip = self.kwargs['ip']

        # geolocate the ip
        location = algorithms.geocode(ip)

        coordinates = []
        coordinates.append(location['latitude'])
        coordinates.append(location['longtitude'])

        context['address'] = location['address']
        context['country'] = location['country']
        context['attacker_ip']= ip

        context["markers"] = {
          "type": "FeatureCollection",
          "crs": {
            "type": "name",
            "properties": {
              "name": "EPSG:4326"
            }
          },
          "features": [
            {
              "id": 1,
              "type": "Feature",
              "properties": {
                "name": "Attacker",
                "pk": "1"
              },
              "geometry": {
                "type": "Point",
                "coordinates": coordinates
              }
            }
          ]
        }
        return context


class LatestHackerView(TemplateView):
    template_name = "latest_map.html"

    def get_context_data(self, **kwargs):

        context = (
            super().get_context_data(
                **kwargs
            )
        )

        # geolocate the ip
        timestamp, ip = algorithms.get_latest_ip()
        location = algorithms.geocode(ip)

        coordinates = []
        coordinates.append(location['latitude'])
        coordinates.append(location['longtitude'])

        context['address'] = location['address']
        context['country'] = location['country']
        context['attacker_ip']= ip
        context['timestamp'] = timestamp

        context["markers"] = {
          "type": "FeatureCollection",
          "crs": {
            "type": "name",
            "properties": {
              "name": "EPSG:4326"
            }
          },
          "features": [
            {
              "id": 1,
              "type": "Feature",
              "properties": {
                "name": ip,
                "pk": "1"
              },
              "geometry": {
                "type": "Point",
                "coordinates": coordinates
              }
            }
          ]
        }
        return context

class LatestSeriesHackerView(TemplateView):
    template_name = "latest_series_map.html"

    def get_context_data(self, **kwargs):

        context = (
            super().get_context_data(
                **kwargs
            )
        )

        # geolocate the ips
        ips = algorithms.get_latest_ips(60)

        # convert them to leaflet features
        features = algorithms.create_features(ips)
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

def SniffLastPeriod(request, period, seconds):

    seconds = int(seconds)
    # write the requested period to the session
    request.session['period-to-check'] = seconds
    request.session['period'] = period

    if seconds == 0:
        return redirect('/sniffers/latest')
    else:
        return redirect('/sniffers')

    #return redirect_with_params('index', period)
