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
            return parse_shapefile_set(self.request.files.getlist('files'))

        files = self.request.files.to_dict()
        f = list(files.values())[0]
        filename = f.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.geojson':
            return parse_geojson(f)
        elif ext == '.kml':
            return parse_kml(f)
        elif ext == '.shp':
            return parse_shp(f)
        elif ext == '.zip':
            return parse_zip(f)
        else:
            return {'error': 'Unrecognized file type'}

# json recursive method modified from: https://stackoverflow.com/questions/21028979/recursive-iteration-through-nested-json-for-specific-key-in-python
def find_elements(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k.lower() == lookup_key.lower():
                yield v
            else:
                yield from find_elements(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from find_elements(item, lookup_key)

def parse_geojson(f):
    try:
        data = f.read()
        geojson = json.loads(data)
    except InvalidGeoJSONException as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    except KeyError as e:
        return {'error': {'type': 'VALUE', 'report': 'Missing expected key: {0}'.format(str(e))}}
    except ValueError as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    
    # Add all geometries you find to a list. Could be nested deep inside json:
    geometry_objs = []

    # Geometry is just one object
    for geom in find_elements(geojson, "geometry"):
        geometry_objs.append(geom)

    # Geometries is a list of objects
    for geometries in find_elements(geojson, "geometries"):
        for geom in geometries:
            geometry_objs.append(geom)

    if len(geometry_objs) == 0:
        return {'error': {'type': 'VALUE', 'report': 'Could not find any "geometry" or "geometries" in geojson.'}}
    elif len(geometry_objs) == 1:
        wkt_str = wkt.dumps(geometry_objs[0])
        return repairWKT(wkt_str)
    # else len(geometry_objs) > 1:

    # Combine all the points of each object into one:
    all_coords = "["
    for geom in geometry_objs:
        # Matches sets like: "[5.304, .5]" or "[623, 9.]"
        match_coords = r'(\[\s*((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*,\s*((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*\])'
        cords = re.findall(match_coords,str(geom["coordinates"]))
        for i, cord in enumerate(cords):
            # Not sure why this is a 2D array, (ie. [i][0]). Maybe a regex fix here...
            all_coords += str(cords[i][0]) + ","
    # Take off the last cooma, add the last brace:
    all_coords = str(all_coords)[0:-1] + "]"
    if all_coords == "[]":
        # This gets hit on for loop not finding any coords to add 
        return {'error': {'type': 'VALUE', 'report': 'Could not find/parse any "coordinates" fields in geojson.'}}
    wkt_json = json.loads('{"type": "MultiPoint", "properties": {}, "coordinates": ' + all_coords + '}')
    # convex_hull will make the shape point if one coord, line for two, and poly for three+
    wkt_str = str(shape(wkt_json).convex_hull)

    return repairWKT(wkt_str)

def parse_kml(f):
    return 'kml'

def parse_shp(f):
    with BytesIO(f.read()) as file:
        sf = shapefile.Reader(shp=file)
        shapeType = sf.shapeTypeName.upper()
        if shapeType not in ['POINT', 'POLYLINE', 'POLYGON']:
            return {'error': {'type': 'VALUE', 'report': 'Invalid shape type, must be point, polyline, or polygon'}}
        geom = sf.shape(0)

    coords = ','.join([' '.join([str(p) for p in c]) for c in geom.points])
    if shapeType == 'POLYGON':
        wkt_str = 'POLYGON(({0}))'.format(coords)
    elif shapeType == 'POLYLINE':
        wkt_str = 'LINESTRING({0})'.format(coords)
    elif shapeType == 'POINT':
        wkt_str = 'POINT({0})'.format(coords)
    else:
        return {'error': {'type': 'VALUE', 'report': 'Invalid shape type, must be point, polyline, or polygon'}}

    return repairWKT(wkt_str)

def parse_zip(f):
    with BytesIO(f.read()) as file:
        zip_obj = zipfile.ZipFile(file)
        parts = zip_obj.namelist()
        for p in parts:
            ext = os.path.splitext(p)[1].lower()
            if ext == '.shp':
                shp_file = BytesIO(zip_obj.read(p))
            elif ext == '.dbf':
                dbf_file = BytesIO(zip_obj.read(p))
            elif ext == '.shx':
                shx_file = BytesIO(zip_obj.read(p))
        sf = shapefile.Reader(shp=shp_file, shx=shx_file, dbf=dbf_file)
    wkt_str = wkt.dumps(sf.shape(0).__geo_interface__)

    return repairWKT(wkt_str)

def parse_shapefile_set(files):
    logging.debug(files)
    for p in files:
        ext = os.path.splitext(p.filename)[1].lower()
        if ext == '.shp':
            shp_file = BytesIO(p.read())
        elif ext == '.dbf':
            dbf_file = BytesIO(p.read())
        elif ext == '.shx':
            shx_file = BytesIO(p.read())

    sf = shapefile.Reader(shp=shp_file, shx=shx_file, dbf=dbf_file)
    wkt_str = wkt.dumps(sf.shape(0).__geo_interface__)

    return repairWKT(wkt_str)
