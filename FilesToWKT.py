from flask import Response
import logging
import json
from geomet import wkt, InvalidGeoJSONException
from io import BytesIO
import shapefile
import zipfile
import api_headers
import os
import re
from APIUtils import repairWKT
from shapely.geometry import shape
from kml2geojson import build_feature_collection as kml2json
import xml.dom.minidom as md


class FilesToWKT:

    def __init__(self, request):
        self.request = request  # store the incoming request

    def get_response(self):
        d = api_headers.base(mimetype='application/json')

        resp_dict = self.make_response()

        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d)

    def make_response(self):
        if 'files' not in self.request.files or len(list(self.request.files.getlist('files'))) < 1:
            return {'error': 'No files provided in files= parameter'}

        if len(list(self.request.files.getlist('files'))) > 1:
            return repairWKT(parse_shapefile_set(self.request.files.getlist('files')))

        files = self.request.files.to_dict()
        f = list(files.values())[0]
        filename = f.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.geojson':
            return repairWKT(parse_geojson(f))
        elif ext == '.kml':
            return repairWKT(parse_kml(f))
        elif ext == '.shp':
            return repairWKT(parse_shp(f))
        elif ext == '.zip':
            return repairWKT(parse_shapefile_zip(f))
        else:
            return {'error': 'Unrecognized file type'}

# def recurse_find_geojson_v2(json_input):
    

# json recursive method modified from: https://stackoverflow.com/questions/21028979/recursive-iteration-through-nested-json-for-specific-key-in-python
def recurse_find_geojson(json_input):
    if isinstance(json_input, type({})):
        # If it's a dict, try to load the minimal required for a shape.
        # Then recurse on every object, just incase more are hiding:
        try:
            shape = { "type": json_input["type"], "coordinates": json_input["coordinates"] }
            yield shape
        except KeyError:
            pass
        for k, v in json_input.items():
            yield from recurse_find_geojson(v)
    # If it's a list, just loop through it:
    elif isinstance(json_input, type([])):
        for item in json_input:
            yield from recurse_find_geojson(item)

def json_to_wkt(geojson):
    geojson_list = []
    for shape in recurse_find_geojson(geojson):
        geojson_list.append(shape)

    if len(geojson_list) == 0:
        return {'error': {'type': 'VALUE', 'report': 'Could not find any shapes inside geojson.'}}
    elif len(geojson_list) == 1:
        wkt_json = geojson_list[0]
    else:
        wkt_json = { 'type': 'GeometryCollection', 'geometries': geojson_list }

    try:
        wkt_str = wkt.dumps(wkt_json)
    #########
    # TODO: Look up exactly what can go wrong ^here^
    #########
    except Exception as e:
        return {'error': {'type': 'VALUE', 'report': 'Problem converting a shape to string: {0}'.format(str(e))}}
    return wkt_str


def parse_geojson(f):
    try:
        data = f.read()
        geojson = json.loads(data)
    except json.JSONDecodeError as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    except KeyError as e:
        return {'error': {'type': 'VALUE', 'report': 'Missing expected key: {0}'.format(str(e))}}
    except ValueError as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    return json_to_wkt(geojson)




def parse_kml(f):
    kml_str = f.read()
    kml_root = md.parseString(kml_str)
    wkt_json = kml2json(kml_root)
    return json_to_wkt(wkt_json)

def parse_shp(f):
    fileset = {'shp': BytesIO(f.read())}
    return parse_shapefile(fileset)

def parse_shapefile_zip(f):
    with BytesIO(f.read()) as file:
        fileset = {}
        zip_obj = zipfile.ZipFile(file)
        parts = zip_obj.namelist()
        for p in parts:
            ext = os.path.splitext(p)[1].lower()
            if ext == '.shp':
                fileset['shp'] = BytesIO(zip_obj.read(p))
            elif ext == '.dbf':
                fileset['dbf'] = BytesIO(zip_obj.read(p))
            elif ext == '.shx':
                fileset['shx'] = BytesIO(zip_obj.read(p))

    return parse_shapefile(fileset)

def parse_shapefile_set(files):
    fileset = {}
    for p in files:
        ext = os.path.splitext(p.filename)[1].lower()
        if ext == '.shp':
            fileset['shp'] = BytesIO(p.read())
        elif ext == '.dbf':
            fileset['dbf'] = BytesIO(p.read())
        elif ext == '.shx':
            fileset['shx'] = BytesIO(p.read())

    return parse_shapefile(fileset)

def parse_shapefile(fileset):
    sf = shapefile.Reader(**fileset)
    wkt_str = wkt.dumps(sf.shape(0).__geo_interface__)
    return wkt_str
