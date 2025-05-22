import os

import Parser
import Tracer
import Plotter

Directory = os.path.abspath(os.path.dirname(__file__))
SavePath = os.path.join(Directory, 'North America')
InputFile = os.path.join(SavePath, 'Export.json')
TracksFile = os.path.join(SavePath, 'Tracks.json')
StationsFile = os.path.join(SavePath, 'Stations.json')
LinesFile = os.path.join(SavePath, 'Lines.json')

ParseData = True
CreateLines = True
PlotNetwork = True
PlotLines = True

if ParseData:
    Parser.SaveTracks(InputFile, TracksFile)
    Parser.SaveStations(InputFile, StationsFile)

if CreateLines:
    Tracer.SaveLines(TracksFile, LinesFile, SavePath)

if PlotNetwork:
    Plotter.NetworkMap(TracksFile, StationsFile, SavePath)

if PlotLines:
    Plotter.TransportMap(SavePath)