import os,glob
from django.conf import settings
from django.db.models import Q
from ..models import Place
from django.conf import settings
from pykml import parser

KML_NAMESPACE = {"kml": "http://earth.google.com/kml/2.0"}

def search_records(country, search):
    # records selected by country and free form search string

    if not search:
        return Place.objects.filter(country__icontains=country)

    places = Place.objects.filter(
        Q(name__icontains=search) |
        Q(type__icontains=search) |
        Q(region__icontains=search) |
        Q(description__icontains=search),
        country__icontains=country)

    return places


def get_current_filter_values(request):
    # first check the dropdown buttons
    # when they are changed, put the new value on the session... otherwise read the old value from the session
    country = request.GET.get('country', None)
    if country:
        request.session['country'] = country
    else:
        try:
            country = request.session['country']
        except:
            country = "Netherlands"
            request.session['country'] = country
    # if all else fails
    if not country:
        country = "Netherlands"

    place_type = request.GET.get('place_type', None)
    if place_type:
        request.session['place_type'] = place_type
    else:
        try:
            place_type = request.session['place_type']
        except:
            place_type = "Stone Circle"
            request.session['place_type'] = place_type
    # if all else fails
    if not place_type:
        place_type = "Stone Circle"

    search = request.GET.get('ancients_search_box', None)
    if not search:
        search = place_type

    return country,place_type,search


def select_records(country, type):
    # records selected by selecting country and type from dropdown lists (so no free form)
    if country == 'All':
        places = Place.objects.filter(type__icontains=type)
    else:
        if type == 'All':
            places = Place.objects.filter(country=country)
        else:
            places = Place.objects.filter(country=country,type__icontains=type)
    return places


def create_features(places):

    features = []

    for place in places:
        # skip records with 0,0 coordinates (like 'all')
        if place.latitude != 0:
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


def read_from_description(separator,description):
    """
      <description>
          <![CDATA[
            <b>Type:</b> Ancient Mine, Quarry or other Industry
            <b>County/Region:</b> Gelderland
            <b>Alt Name:</b> Vuursteenwerkplaats
            <br />
            Pos Accuracy: <b>4</b>
            Ambience: <b>3</b>  (5 is best)
            <br />
            <b>Lat:</b> 52.19213 &nbsp;&nbsp;&nbsp;
            <b>Long</b>: 5.60222
            <br />
            During work on the road in 2018 several archaeological finds were made, amongst which a Mesolithic flint workshop. There is an information board about the finds.. ...<b>.</b> (c) Meg. Portal contributors.<br />
            <a href="http://www.megalithic.co.uk/article.php?sid=61013" >Link To More Information</a><br />
          ]]>
        </description>
    """
    try:
        s = description.split(separator)
        s2 = s[1].split('<b>')
        s3 = s2[0]
        if "<br /> Pos Accuracy:" in s3:
            s3 = s3.replace("<br /> Pos Accuracy:","")

        if "<br />Condition:" in s3:
            s3 = s3.replace("<br />Condition:","")

        value = s3.strip()
        return value
    except:
        return ""

def convert_kml(kml_filename,country):
    """
    convert a placemark to a json record
    """

    records = []
    with open(kml_filename, 'r', encoding="ISO-8859-1") as f:
        doc = parser.parse(f)
        root = doc.getroot()
        placemarks = root.findall(".//kml:Placemark", KML_NAMESPACE)

        for place in placemarks:

            name = place.name.text.encode('ISO-8859-1').decode('utf-8')
            description = place.description.text
            coordinates = place.Point.coordinates.text
            latitude = float(coordinates.split(',')[1])
            longtitude = float(coordinates.split(',')[0])

            # retrieve type from description
            type = read_from_description('<b>Type:</b>',description)
            region = read_from_description('<b>County/Region:</b>',description)
            country = country
            rec = (name, type, region, country, latitude, longtitude, description)
            records.append(rec)

        return records

def reload_data():
    # look for kml files in the data directory
    fake_it = False

    directory = settings.DATA_ROOT
    print(directory)

    # clear the ancients.sqlite3 database (scary)
    if not fake_it:
        Place.objects.all().delete()



    for kml_file in glob.glob(os.path.join(directory, "*.kml")):
        filename = os.path.basename(kml_file)

        if filename.startswith("MegP_"):

            # only take into account files with the pattern "MegP_<country>.kml
            country = ".".join(filename.split("_", 1)[1].split(".")[:-1])

            # convert the kml file to a list of records
            records = convert_kml(kml_file,country)
            print(f'{filename} => {country}: {len(records)}... adding to database')

            # add an 'all' record for the selection dropdown boxes
            place = Place(type="All", country=country, latitude=0, longtitude=0)
            if not fake_it:
                place.save()

            # insert the records into the ancients.sqlite3 database
            for record in records:
                place = Place(
                    name=record[0],
                    type=record[1],
                    region=record[2],
                    country=record[3],
                    latitude=record[4],
                    longtitude=record[5],
                    description=record[6],
                )
                if not fake_it:
                    place.save()