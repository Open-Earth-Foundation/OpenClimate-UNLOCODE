#!/usr/bin/python
# unlocode_to_openclimate.py -- convert UNLOCODE data to OpenClimate format

import csv

INPUT_DIR = 'loc221csv'
OUTPUT_DIR = 'UNLOCODE'

PUBLISHER = {
    "id": "UNECE",
    "name": "United Nations Economic Commission for Europe (UNECE)",
    "URL": "https://unece.org/"
}

DATASOURCE = {
    "datasource_id": "UNLOCODE:2022-1",
    "name": "UN/LOCODE (CODE FOR TRADE AND TRANSPORT LOCATIONS) Issue 2022-1",
    "publisher": PUBLISHER["id"],
    "published": "2022-07-08",
    "URL": "https://unece.org/trade/uncefact/unlocode"
}

LOCODE_COLUMNS = [
  "Ch",
  "ISO 3166-1",
  "LOCODE",
  "Name",
  "NameWoDiacritics",
  "SubDiv",
  "Function",
  "Status",
  "Date",
  "IATA",
  "Coordinates",
  "Remarks"
]

ACTOR_COLUMNS = [
    "actor_id",
    "type",
    "name",
    "is_part_of",
    "datasource_id"
]

ACTOR_NAME_COLUMNS = [
    "actor_id",
    "name",
    "language",
    "preferred",
    "datasource_id"
]

TERRITORY_COLUMNS = [
    "actor_id",
    "lat",
    "lng",
    "datasource_id"
]

def write_csv(name, rows):
    with open(f'{OUTPUT_DIR}/{name}.csv', mode='w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def prepare_output_file(name, column_names):
    with open(f'{OUTPUT_DIR}/{name}.csv', mode='w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()

def write_output_row(filename, column_names, row):
    with open(f'{OUTPUT_DIR}/{filename}.csv', mode='a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writerow(row)

def coordinates_to_decimal(coords):

    lat_deg = int(coords[0:2])
    lat_min = int(coords[2:4])
    lat_dir = coords[4:5]

    lat = round(lat_deg*10000 + (lat_min*10000)/60) * (-1 if lat_dir == "S" else 1)

    lng_deg = int(coords[6:9])
    lng_min = int(coords[9:11])
    lng_dir = coords[11:12]

    lng = round(lng_deg*10000 + (lng_min*10000)/60) * (-1 if lng_dir == "W" else 1)

    return (lat, lng)

def handle_input_row(row):

    # Skip if no LOCODE

    if row["LOCODE"] == "":
        return

    # Test for function = road station; not perfect but...

    if len(row['Function']) < 3 or row['Function'][2] != "3":
        return

    actor_id = f'{row["ISO 3166-1"]}-{row["LOCODE"]}'
    parent_id = f'{row["ISO 3166-1"]}-{row["SubDiv"]}' if row["SubDiv"] != '' else row["ISO 3166-1"]

    write_output_row("Actor", ACTOR_COLUMNS, {
        "actor_id": actor_id,
        "type": "city",
        "name": row["Name"],
        "is_part_of": parent_id,
        "datasource_id": DATASOURCE["datasource_id"]
    })

    write_output_row("ActorName", ACTOR_NAME_COLUMNS, {
        "actor_id": actor_id,
        "name": row["Name"],
        "language": "und",
        "preferred": 0,
        "datasource_id": DATASOURCE["datasource_id"]
    })

    if (row["NameWoDiacritics"] != row["Name"]):
        write_output_row("ActorName", ACTOR_NAME_COLUMNS, {
            "actor_id": actor_id,
            "name": row["NameWoDiacritics"],
            "language": "und",
            "preferred": 0,
            "datasource_id": DATASOURCE["datasource_id"]
        })

    if row["Coordinates"] != "":
        (lat, lng) = coordinates_to_decimal(row["Coordinates"])
        write_output_row("Territory", TERRITORY_COLUMNS, {
            "actor_id": actor_id,
            "lat": lat,
            "lng": lng,
            "datasource_id": DATASOURCE["datasource_id"]
        })

def main():

    write_csv('Publisher', [PUBLISHER])
    write_csv('DataSource', [DATASOURCE])

    prepare_output_file('Actor', ACTOR_COLUMNS)
    prepare_output_file('ActorName', ACTOR_NAME_COLUMNS)
    prepare_output_file('Territory', TERRITORY_COLUMNS)

    for i in [1, 2, 3]:
        with open(f'{INPUT_DIR}/2022-1 UNLOCODE CodeListPart{i}.csv') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=LOCODE_COLUMNS)
            for row in reader:
                handle_input_row(row)


if __name__ == "__main__":
    main()