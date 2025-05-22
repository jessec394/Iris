import folium
import json
import os
from xml.etree import ElementTree as ET

def GenerateMap():
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri",
        name="Esri World Imagery"
    ).add_to(m)
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('CartoDB Positron', name="CartoDB Positron", overlay=False).add_to(m)

    return m

def NetworkMap(TracksFile, StationsFile, SavePath, Accuracy=1e-4):
    m = GenerateMap()

    with open(TracksFile, 'r') as f: Tracks = json.load(f)

    for track in Tracks:
        Coordinates = track['coordinates']
        SimplifiedCoords = []
        LastPoint = None
        for lon, lat in Coordinates:
            if LastPoint is None or abs(lon - LastPoint[0]) > Accuracy or abs(lat - LastPoint[1]) > Accuracy:
                SimplifiedCoords.append([lat, lon])
                LastPoint = (lon, lat)

        folium.PolyLine(
            locations=SimplifiedCoords,
            color="blue",
            weight=2.5,
            opacity=0.8
        ).add_to(m)

    with open(StationsFile, 'r') as f:
        Stations = json.load(f)

    for station in Stations:
        Name = station.get('name', 'Unknown')
        Coordinates = station.get('coordinates', [0, 0])

        if isinstance(Coordinates[0], list):
            Coordinates = Coordinates[0]
        if len(Coordinates) == 2:
            lat, lon = Coordinates[1], Coordinates[0]
            # folium.Marker(
            #     location=[lat, lon],
            #     popup=Name,
            #     icon=folium.Icon(color='red', icon='info-sign')
            # ).add_to(m)

    folium.LayerControl().add_to(m)
    folium.LatLngPopup().add_to(m)
    folium.ClickForMarker(popup=None).add_to(m)

    m.save(os.path.join(SavePath, 'Network Map.html'))

def TransportMap(SavePath, Accuracy=1e-5):
    m = GenerateMap()

    LinesPath = os.path.join(SavePath, 'Lines')

    LineStyles = {
        "APM": {"color": "#b1b1b1", "weight": 2, "size": 3},
        "Tram": {"color": "#006a90", "weight": 2, "size": 3},
        "Light Rail": {"color": "#00beff", "weight": 2, "size": 3},
        "Light Metro": {"color": "#ffba00", "weight": 3, "size": 5},
        "Heavy Metro": {"color": "#ff0000", "weight": 3, "size": 7},
        "Heavy Rail": {"color": "#6400ff", "weight": 4, "size": 7},
        "Intercity Rail": {"color": "#1e81b0", "weight": 5, "size": 10},
        "High-Speed Rail": {"color": "#063970", "weight": 6, "size": 12},
    }

    Legend = ''.join([
        f'<div style="display: flex; align-items: center; margin-top:8px;">'
        f'<i class="fa fa-minus" style="color:{v["color"]}; font-size:18px;"></i>'
        f'<span style="margin-left:10px;">{k}</span></div>' for k, v in LineStyles.items()
    ])
    Legend = f'<div style="position: fixed; bottom: 50px; left: 50px; width: 240px; background-color: rgba(0, 0, 0, 0.7); border-radius: 8px; padding: 15px; color: white; font-size:14px; font-family: Arial, sans-serif; z-index:9999; box-shadow: 3px 3px 15px rgba(0, 0, 0, 0.4);">{Legend}</div>'

    if os.path.exists(LinesPath):
        for filename in os.listdir(LinesPath):
            if filename.endswith('.kml'):
                FilePath = os.path.join(LinesPath, filename)

                try:
                    line_type = filename.split(']')[0][1:]
                except IndexError:
                    continue

                Style = LineStyles.get(line_type, {"color": "#000000", "weight": 2, "size": 3})

                Tree = ET.parse(FilePath)
                Root = Tree.getroot()
                NS = {'kml': 'http://www.opengis.net/kml/2.2'}

                for placemark in Root.findall('.//kml:Placemark', NS):
                    Coordinates = placemark.find('.//kml:coordinates', NS)
                    if Coordinates is not None:
                        CoordsList = Coordinates.text.strip().split()
                        SimplifiedCoords = []
                        LastPoint = None

                        for coord in CoordsList:
                            Lon, Lat, *_ = map(float, coord.split(','))
                            if LastPoint is None or abs(Lon - LastPoint[0]) > Accuracy or abs(Lat - LastPoint[1]) > Accuracy:
                                SimplifiedCoords.append([Lat, Lon])
                                LastPoint = (Lon, Lat)

                        if SimplifiedCoords:
                            folium.PolyLine(
                                locations=SimplifiedCoords,
                                color=Style["color"],
                                weight=Style["weight"],
                                opacity=1.0
                            ).add_to(m)

    folium.LayerControl().add_to(m)
    m.get_root().html.add_child(folium.Element(Legend))

    m.save(os.path.join(SavePath, 'Transport Map.html'))