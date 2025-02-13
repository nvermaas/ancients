from django.conf import settings
from ..models import Place

def create_features():

    features = []
    places = Place.objects.all()

    for place in places:
        try:

            coordinates = []
            coordinates.append(place.longtitude)
            coordinates.append(place.latitude)

            feature = {}
            feature['id'] = place.id
            feature['type'] = 'Feature'

            properties = {}
            properties['name'] = f'<H5>{place.name}</H5><hr>{place.description}'
            properties['pk'] = place.id

            #properties['color'] = 'green'
            #properties['radius'] = 4

            feature['properties'] = properties

            geometry = {}
            geometry['type'] = "Point"
            geometry['coordinates'] = coordinates

            feature['geometry'] = geometry

            features.append(feature)
        except:
            pass

    return features