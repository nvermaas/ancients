from django.conf import settings
from ..models import Place

def create_features(places):

    features = []

    for place in places:
        try:

            coordinates = []
            coordinates.append(place.latitude)
            coordinates.append(place.longtitude)

            feature = {}
            feature['id'] = place.id
            feature['type'] = 'Feature'

            properties = {}
            properties['name'] = place.name
            properties['pk'] = place.id

            if location['new'] == True:
                properties['color'] = 'red'
                properties['radius'] = 8
            else:
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