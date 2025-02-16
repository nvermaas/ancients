from django.conf import settings
from django.db.models import Q
from ..models import Place

def get_searched_records(q):
    if not q:
        return Place.objects.all()

    records = Place.objects.filter(
        Q(name__icontains=q) |
        Q(type__icontains=q) |
        Q(region__icontains=q) |
        Q(description__icontains=q))

    return records

def create_features(search):

    features = []
    places = get_searched_records(search)

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