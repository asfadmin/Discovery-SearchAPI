from flask import Response
import logging
import json
from geomet import wkt, InvalidGeoJSONException
import api_headers
import os
from APIUtils import repairWKT

class FilesToWKT:

    def __init__(self, request):
        self.request = request  # store the incoming request

    def get_response(self):
        d = api_headers.base(mimetype='application/json')

        resp_dict = self.make_response()

        return Response(json.dumps(resp_dict), 200, headers=d)

    def make_response(self):
        if 'files' not in self.request.files:
            return {'error': 'No files provided in files= parameter'}
        files = self.request.files.to_dict()
        for f in files:
            filename = files[f].filename
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.geojson':
                return parse_geojson(files[f])
            elif ext == '.kml':
                return parse_kml(files[f])
            elif ext == '.shp':
                return parse_shapefile(files[f])
            else:
                return {'error': 'Unrecognized file type'}
            logging.debug(filename)
        return 'cool'

def parse_geojson(f):
    try:
        data = f.read()
        geom = json.loads(data)['features'][0]['geometry']
        wkt_str = wkt.dumps(geom)
    except InvalidGeoJSONException as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    except KeyError as e:
        return {'error': {'type': 'VALUE', 'report': 'Missing expected key: {0}'.format(str(e))}}
    except ValueError as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    return repairWKT(wkt_str)

def parse_kml(f):
    return 'kml'

def parse_shapefile(f):
    return 'shapefile'
