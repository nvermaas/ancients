import sys
import datetime
import time
from pykml import parser
import sqlite3

KML_NAMESPACE = {"kml": "http://earth.google.com/kml/2.0"}

create_places = """
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        region TEXT,
        latitude FLOAT,
        longtitude FLOAT,
        description TEXT
    )
    """

def create_database(sqlite_filename, records):
    conn = sqlite3.connect(sqlite_filename)  # Creates or opens a database file
    cursor = conn.cursor()  # Create a cursor object to interact with the database

    cursor.execute(create_places)
    conn.commit()

    print(f'adding {len(records)} records to database {sqlite_filename}...')
    cursor.executemany("INSERT INTO places (name, type, region, latitude, longtitude, description) VALUES (?, ?, ?, ?, ?, ?)", records)
    conn.commit()

    print('done')
    conn.close()

def add_to_database(sqlite_filename, records):
    conn = sqlite3.connect(sqlite_filename)  # Creates or opens a database file
    cursor = conn.cursor()  # Create a cursor object to interact with the database

    print(f'adding {len(records)} records to database {sqlite_filename}...')
    cursor.executemany("INSERT INTO places_place (name, type, region, latitude, longtitude, description) VALUES (?, ?, ?, ?, ?, ?)", records)
    conn.commit()

    print('done')
    conn.close()

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

def convert_kml(kml_filename):
    """
    convert a placemark to a json record

    <Placemark>
       <name>Flint workshop Voorthuizen</name>
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
        <styleUrl>#31_g</styleUrl>
        <Point>
           <coordinates>5.60222,52.19213,0</coordinates>
        </Point>
    </Placemark>
    """

    # https://pythonhosted.org/pykml/tutorial.html#parsing-existing-kml-documents

    records = []

    with open(kml_filename, 'r', encoding="ISO-8859-1") as f:
        doc = parser.parse(f)
        root = doc.getroot()
        placemarks = root.findall(".//kml:Placemark", KML_NAMESPACE)

        print('converting...')
        for place in placemarks:

            name = place.name.text
            description = place.description.text
            coordinates = place.Point.coordinates.text
            latitude = float(coordinates.split(',')[1])
            longtitude = float(coordinates.split(',')[0])

            # retrieve type from description
            type = read_from_description('<b>Type:</b>',description)
            region = read_from_description('<b>County/Region:</b>',description)

            rec = (name, type, region, latitude, longtitude, description)
            records.append(rec)

        print(f'read {len(records)} records')
        return records


if __name__ == "__main__":
    header = "megp_kml_convert - version 1  Fan 2025"
    print(header)
    print("--------------------------------")

    if len(sys.argv) != 4:
        print("Usage: python megp_kml_convert.py <kml_file> <sqlite_file> <mode>\n")
        print("examples:")
        print("- python megp_kml_convert.py MegP_Netherlands.kml ancients.sqlite add")
        print("- python megp_kml_convert.py megalithic_earth.kml ancients.sqlite clear")

        sys.exit(1)

    print(f"input = {sys.argv[1]}, output = {sys.argv[2]}, mode = {sys.argv[3]}")
    # Retrieve parameters from command-line arguments

    input  = sys.argv[1]
    output = sys.argv[2]
    mode = sys.argv[3]

    # convert the kml to a dict of records
    records = convert_kml(input)

    # creat and fill database
    if mode == 'new':
        create_database(output,records)

    if mode == 'add':
        add_to_database(output,records)

    #convert(input, output, mode)
