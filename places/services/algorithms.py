import os,glob

import requests
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from ..models import Place, Dataset
from django.conf import settings
from pykml import parser

KML_NAMESPACE = {"kml": "http://earth.google.com/kml/2.0"}

CIRCLES = ["Circle","Henge"]
STONES = ["Stone","Polissoir","Alignement","Cairn"]
GRAVES = ["Barrow","Tomb","Grave","Cist","Dolmen","Burial"]
HILLS = ["Mound","Hill","Cursus","Pyramid"]
NATURAL = ["Natural","Rock Outcrop"]
VILLAGES = ["Village","Settlement","Town","Crannog","Broch"]
CAVES = ["Cave","Rock Shelter"]
CROSSES = ["Cross"]
SPRINGS = ["Well","Spring"]
MUSEUMS = ["Museum"]
FORTS = ["Fort","Castro"]
INDUSTRY = ["Mine","Quarry"]
TEMPLES = ["Temple","Palace"]
TRACKS = ["Track","Causeway"]
ART = ["Carving","Art"]
MAZES = ['Maze']
UNKNOWN = ['Unknown',"Not Known"]

COMBINATIONS = {
    "Art": ART,
    "Caves": CAVES,
    "Circles"   : CIRCLES,
    "Crosses": CROSSES,
    "Graves"    : GRAVES,
    "Forts": FORTS,
    "Hills": HILLS,
    "Industry": INDUSTRY,
    "Mazes": MAZES,
    "Museums": MUSEUMS,
    "Natural features" : NATURAL,
    "Springs"   : SPRINGS,
    "Stones"    : STONES,
    "Temples"   : TEMPLES,
    "Tracks"    : TRACKS,
    "Villages":   VILLAGES,
    "Unknown"   : UNKNOWN
}

def get_category(type_value):
    for category, items in COMBINATIONS.items():
        if any(item.upper() in type_value.upper() for item in items):
            return category

    return "Other"

def search_records(search):

    places = Place.objects.filter(
        Q(name__icontains=search) |
        Q(type__icontains=search) |
        Q(region__icontains=search))

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


    category = request.GET.get('category', None)
    if category:
        request.session['category'] = category
    else:
        try:
            category = request.session['category']
        except:
            category = "Stones"
            request.session['category'] = category

    # if all else fails
    if not category:
        category = "Stones"


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

    return country,category,place_type,search


def select_records(country, category, type, search):

    # if a specific search is given, then look for it. Otherwise use the dropdown values
    if search:
        places = search_records(search)

    else:
        # records selected by selecting country and type from dropdown lists (so no free form)
        if country == 'All':
            places = Place.objects.filter(type__icontains=type)
        else:
            if type == 'All':
                places = Place.objects.filter(country=country)
                places = Place.objects.filter(country=country, category__icontains=category)
            else:
                places = Place.objects.filter(country=country,type__icontains=type)
                # places = Place.objects.filter(country=country, category__icontains=category)


    return places.exclude(type="All")


def create_features(places):

    features = []

    for place in places[:settings.MAX_FEATURES]:
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


def convert_kml_file(kml_filename, country):
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
            category = get_category(type)
            region = read_from_description('<b>County/Region:</b>',description)
            country = country
            rec = (name, category, type, region, country, latitude, longtitude, description)
            records.append(rec)

        return records

def update_dataset(country):
    # load the kml and parse it

    dataset = Dataset.objects.get(country=country)
    directory = settings.DATA_ROOT

    # mimic a browser request:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    # construct the url
    if dataset.url:
        url = dataset.url
    else:
        url = f"https://www.megalithic.co.uk/asb_kml.php?category=0&country={dataset.country_nr}&sitetype=0&kmltitle={dataset.country}"

    if dataset.filename:
        filename = dataset.filename
    else:
        filename = f"MegP_{dataset.country}.kml"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        file_path = os.path.join(directory,filename)
        # Write content to a .kml file
        with open(file_path, "wb") as file:
            file.write(response.content)

        # convert the kml file to a list of records
        records = convert_kml_file(file_path, country)
        count = len(records)
        print(f'{country}: {count}... adding to database')

        if count > 0:
            # delete the existing records
            Place.objects.filter(country=country).delete()

            # add an 'all' record for the selection dropdown boxes
            place = Place(type="All", category="All", country=country, latitude=0, longtitude=0)
            place.save()

            # add the records to the sqlite3 database
            for record in records:
                place = Place(
                    name=record[0],
                    category=record[1],
                    type=record[2],
                    region=record[3],
                    country=record[4],
                    latitude=record[5],
                    longtitude=record[6],
                    description=record[7],
                )
                place.save()

            # update dataset record
            dataset.timestamp = timezone.now()
            dataset.count = count
            dataset.save()


def reload_data():
    # look for kml files in the data directory
    # note: to shrink the database by reclaiming removed records, use the sql 'vacuum' command
    fake_it = False

    directory = settings.DATA_ROOT
    print(directory)

    # clear the ancients.sqlite3 database (scary)
    if not fake_it:
        Place.objects.all().delete()

    # add an 'all' record for the selection dropdown boxes
    place = Place(type="All", category="All", country="All", latitude=0, longtitude=0)
    if not fake_it:
        place.save()

    for kml_file in glob.glob(os.path.join(directory, "*.kml")):
        filename = os.path.basename(kml_file)

        if filename.startswith("MegP_"):

            # only take into account files with the pattern "MegP_<country>.kml
            country = ".".join(filename.split("_", 1)[1].split(".")[:-1])

            # convert the kml file to a list of records
            records = convert_kml_file(kml_file, country)
            print(f'{filename} => {country}: {len(records)}... adding to database')

            # add an 'all' record for the selection dropdown boxes
            place = Place(type="All", category="All", country=country, latitude=0, longtitude=0)
            if not fake_it:
                place.save()

            # insert the records into the ancients.sqlite3 database
            for record in records:
                place = Place(
                    name=record[0],
                    category=record[1],
                    type=record[2],
                    region=record[3],
                    country=record[4],
                    latitude=record[5],
                    longtitude=record[6],
                    description=record[7],
                )
                if not fake_it:
                    place.save()