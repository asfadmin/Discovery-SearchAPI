import logging
import json
from .json import JSONStreamArray

def cmr_to_geojson(rgen, includeBaseline=False, addendum=None):
    logging.debug('translating: geojson')

    streamer = GeoJSONStreamArray(rgen, includeBaseline)

    for p in json.JSONEncoder(indent=2, sort_keys=True).iterencode({'type': 'FeatureCollection','features':streamer}):
        yield p


class GeoJSONStreamArray(JSONStreamArray):

    def getItem(self, p):
        for i in p.keys():
            if p[i] == 'NA' or p[i] == '':
                p[i] = None
        try:
            if float(p['offNadirAngle']) < 0:
                p['offNadirAngle'] = None
            if float(p['relativeOrbit']) < 0:
                p['relativeOrbit'] = None
        except TypeError:
            pass

        result = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [[float(c['lon']), float(c['lat'])] for c in p['shape']]
                ]
            },
            'properties': {
                'sceneName': p['granuleName'],
                'fileID': p['product_file_id'],
                'platform': p['platform'],
                'sensor': p['sensor'],
                'orbit': p['absoluteOrbit'],
                'offNadirAngle': p['offNadirAngle'],
                'startTime': p['startTime'],
                'stopTime': p['stopTime'],
                'flightDirection': p['flightDirection'],
                'granuleType': p['granuleType'],
                'polarization': p['polarization'],
                'browse': p['browse'],
                'frameNumber': p['frameNumber'],
                'pathNumber': p['relativeOrbit'],
                'beamModeType': p['beamModeType'],
                'faradayRotation': p['faradayRotation'],
                'bytes': p['bytes'],
                'fileName': p['fileName'],
                'md5sum': p['md5sum'],
                'processingDate': p['processingDate'],
                'processingLevel': p['processingLevel'],
                'url': p['downloadUrl']
            }
        }
        if self.includeBaseline:
            result['properties']['temporalBaseline'] = p['temporalBaseline']
            result['properties']['perpendicularBaseline'] = p['perpendicularBaseline']

        return result
