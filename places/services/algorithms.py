from django.conf import settings
from django.db.models import Q
from ..models import Place

def select_records(country, type):
    # records selected by selecting country and type from dropdown lists (so no free form)
    records = Place.objects.filter(country=country,type__icontains=type)
    return records

def search_records(country, search):
    # records selected by country and free form search string

    if not search:
        return Place.objects.filter(country__icontains=country)

    records = Place.objects.filter(
        Q(name__icontains=search) |
        Q(type__icontains=search) |
        Q(region__icontains=search) |
        Q(description__icontains=search),
        country__icontains=country)

    return records

def create_features(country, search):

    features = []
    #places = search_records(country, search)
    places = select_records(country, search)

    for place in places:
        try:

            coordinates = []
            coordinates.append(place.longtitude)
            coordinates.append(place.latitude)

            feature = {}
            feature['id'] = place.id
            feature['type'] = 'Feature'

            properties = {}
            properties['name'] = f'<H3>{place.name}</H3><hr><h5>{place.description}</h5>'
            properties['pk'] = place.id

            properties['color'] = 'green'
            properties['radius'] = 4

            feature['properties'] = properties

            geometry = {}
            geometry['type'] = "Point"
            geometry['coordinates'] = coordinates

            feature['geometry'] = geometry

            features.append(feature)
        except:
            pass

    return features