from flask import Response
import logging
import json
from geomet import wkt, InvalidGeoJSONException
from io import BytesIO
import shapefile
import zipfile
import api_headers
import os
from APIUtils import repairWKT
from kml2geojson import build_feature_collection as kml2json
import defusedxml.minidom as md
# from defusedxml import DefusedXmlException, DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden, NotSupportedError


class FilesToWKT:

    def __init__(self, request):
        self.request = request  # store the incoming request

    def get_response(self):
        d = api_headers.base(mimetype='application/json')

        resp_dict = self.make_response()

        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d)

    def make_response(self):
        args = self.request.args.to_dict()
        should_repair = False if "repair" in args and args['repair'].lower() == 'false' else True

        if 'files' not in self.request.files or len(list(self.request.files.getlist('files'))) < 1:
            return {'error': 'No files provided in files= parameter'}

        if len(list(self.request.files.getlist('files'))) > 1:
            return repairWKT(parse_shapefile_set(self.request.files.getlist('files')))

        files = self.request.files.to_dict()
        f = list(files.values())[0]
        filename = f.filename
        ext = os.path.splitext(filename)[1].lower()
        # GEOJSON
        if ext == '.geojson':
            parsed_geo = parse_geojson(f)
            if "error" in parsed_geo or not should_repair:
                return parsed_geo
            return repairWKT(parsed_geo)
        # KML
        elif ext == '.kml':
            parsed_kml = parse_kml(f)
            if "error" in parsed_kml or not should_repair:
                return parsed_kml
            return repairWKT(parsed_kml)
        # SHP
        elif ext == '.shp':
            parsed_shp = parse_shp(f)
            if "error" in parsed_shp or not should_repair:
                return parsed_shp
            return repairWKT(parsed_shp)

        elif ext == '.zip':
            parsed_zip = parse_shapefile_zip(f)
            if "error" in parsed_zip or not should_repair:
                return parsed_zip
            return repairWKT(parsed_zip)
        else:
            return {'error': 'Unrecognized file type'}
    

# Takes any json, and returns a list of all {"type": x, "coordinates": y} objects 
# found, ignoring anything else in the block
def recurse_find_geojson(json_input):
    if isinstance(json_input, type({})):
        # If it's a dict, try to load the minimal required for a shape.
        # Then recurse on every object, just incase more are nested inside:
        try:
            new_shape = { "type": json_input["type"], "coordinates": json_input["coordinates"] }
            yield new_shape
        except KeyError:
            pass
        for key_value_pair in json_input.items():
            yield from recurse_find_geojson(key_value_pair[1])
    # If it's a list, just loop through it:
    elif isinstance(json_input, type([])):
        for item in json_input:
            yield from recurse_find_geojson(item)

# Takes a json, and returns a possibly-simplified wkt_str
# Used by both parse_geojson, and parse_kml
def json_to_wkt(geojson):
    geojson_list = []
    for new_shape in recurse_find_geojson(geojson):
        geojson_list.append(new_shape)

    if len(geojson_list) == 0:
        return {'error': {'type': 'VALUE', 'report': 'Could not find any shapes inside geojson.'}}
    elif len(geojson_list) == 1:
        wkt_json = geojson_list[0]
    else:
        wkt_json = { 'type': 'GeometryCollection', 'geometries': geojson_list }

    try:
        wkt_str = wkt.dumps(wkt_json)
    except (KeyError, ValueError) as e:
        return {'error': {'type': 'VALUE', 'report': 'Problem converting a shape to string: {0}'.format(str(e))}}
    return wkt_str


def parse_geojson(f):
    try:
        data = f.read()
        geojson = json.loads(data)
    except json.JSONDecodeError as e:
        return {'error': {'type': 'DECODE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    except KeyError as e:
        return {'error': {'type': 'KEY', 'report': 'Missing expected key: {0}'.format(str(e))}}
    except ValueError as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    return json_to_wkt(geojson)


def parse_kml(f):
    kml_str = f.read()
    try:
        kml_root = md.parseString(kml_str, forbid_dtd=True)
        wkt_json = kml2json(kml_root)
    # All these BUT the type/value errors are for the md.parseString:
    # except (DefusedXmlException, DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden, NotSupportedError, TypeError, ValueError) as e:
    except Exception as e:  
        return {'error': {'type': 'VALUE', 'report': 'Could not parse kml: {0}'.format(str(e))}} 
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
    try:
        reader = shapefile.Reader(**fileset)
        shapes = [i.__geo_interface__ for i in reader.shapes()]
    # In the sourcecode, it looks like sometimes the reader throws "Exception":
    except Exception as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse shp: {0}'.format(str(e))}}
    wkt_json = {'type':'GeometryCollection', 'geometries': shapes }
    wkt_str = json_to_wkt(wkt_json)
    return wkt_str
