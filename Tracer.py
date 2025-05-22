import os
import json
import simplekml
from shapely.geometry import LineString, Point

def NearestTrack(Waypoint, Tracks):
    MinDistance = float("inf")
    NearestTrack = None

    for track in Tracks:
        TrackLine = LineString(track["coordinates"])
        Distance = TrackLine.distance(Point(Waypoint[1], Waypoint[0]))

        if Distance < MinDistance:
            MinDistance = Distance
            NearestTrack = track

    return NearestTrack

def TraceRoute(Waypoints, Tracks):
    Route = []

    for i in range(len(Waypoints) - 1):
        WaypointI = Waypoints[i]
        WaypointF = Waypoints[i + 1]

        TrackI = NearestTrack(WaypointI, Tracks)
        TrackF = NearestTrack(WaypointF, Tracks)

        if not TrackI or not TrackF: continue

        CoordsI = TrackI["coordinates"]
        CoordsF = TrackF["coordinates"]

        StartIndex = min(
            range(len(CoordsI)),
            key=lambda idx: Point(CoordsI[idx]).distance(Point(WaypointI[1], WaypointI[0]))
        )

        EndIndex = min(
            range(len(CoordsF)),
            key=lambda idx: Point(CoordsF[idx]).distance(Point(WaypointF[1], WaypointF[0]))
        )

        if TrackI == TrackF:
            if StartIndex <= EndIndex: Route.extend(CoordsI[StartIndex:EndIndex + 1])
            else: Route.extend(CoordsI[StartIndex::-1] + CoordsI[:EndIndex + 1])
        else:
            if StartIndex < len(CoordsI) - 1: Route.extend(CoordsI[StartIndex:])

            NearestTransition = min(
                CoordsF, key=lambda coord: Point(coord).distance(Point(CoordsI[-1]))
            )

            TransitionIndex = CoordsF.index(NearestTransition)

            if TransitionIndex <= EndIndex: Route.extend(CoordsF[TransitionIndex:EndIndex + 1])
            else: Route.extend(CoordsF[TransitionIndex::-1] + CoordsF[:EndIndex + 1])

    return Route

def TrimRoute(route, waypoint):
    for i, (lon, lat) in enumerate(route):
        if (round(lat, 6), round(lon, 6)) == (round(waypoint[0], 6), round(waypoint[1], 6)): return route[i:]
    return route

def SaveKML(Name, Type, Operator, Route, FirstWaypoint, SavePath):
    if FirstWaypoint: Route = TrimRoute(Route, FirstWaypoint)
    if not Route: return

    KML = simplekml.Kml()
    Linestring = KML.newlinestring(name=Name)
    Linestring.coords = [(lon, lat) for lon, lat in Route]
    Linestring.style.linestyle.color = simplekml.Color.blue
    Linestring.style.linestyle.width = 3

    KML.save(os.path.join(SavePath, f"[{Type}] {Operator} {Name}.kml"))

def SaveLines(TracksFile, LinesFile, SavePath):
    with open(TracksFile, 'r') as f: Tracks = json.load(f)
    with open(LinesFile, 'r') as f: Lines = json.load(f)

    LinesPath = os.path.join(SavePath, "Lines")
    os.makedirs(LinesPath, exist_ok=True)

    for line in Lines:
        Operator = line["Operator"]
        Type = line["Type"]
        Name = line["Name"]
        Waypoints = line["Waypoints"]

        FilePath = os.path.join(LinesPath, f"[{Type}] {Operator} {Name}.kml")
        if os.path.exists(FilePath): continue

        Route = TraceRoute(Waypoints, Tracks)
        if Route: SaveKML(Name, Type, Operator, Route, Waypoints[0], LinesPath)