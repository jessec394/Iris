import json
import os
from shapely.geometry import LineString

def SaveTracks(InputFile, SavePath):
    with open(InputFile, 'r') as f: GeoData = json.load(f)

    Tracks = []

    for feature in GeoData['features']:
        if feature['properties']['preview_type'] == 'tracks':
            Coordinates = feature['geometry']['coordinates']
            for track in Coordinates:
                TrackLine = LineString(track)
                CoordsList = [[lon, lat] for lon, lat in TrackLine.coords]
                Tracks.append({"name": "Custom Track", "coordinates": CoordsList})

    with open(SavePath, 'w') as outfile: json.dump(Tracks, outfile, indent=4)

def SaveStations(InputFile, SavePath):
    with open(InputFile, 'r') as f: 
        GeoData = json.load(f)

    Stations = []

    for feature in GeoData['features']:
        if feature['properties']['preview_type'] == 'station':
            station = {
                "id": feature['properties']['id'],
                "name": feature['properties']['name'],
                "coordinates": feature['geometry']['coordinates']
            }
            Stations.append(station)

    with open(SavePath, 'w') as outfile: json.dump(Stations, outfile, indent=4)