import logging
import json
from .json import JSONStreamArray

def req_fields_geojson():
    fields = [
        'beamMode',
        'beamModeType',
        'browse',
        'bytes',
        'centerLat',
        'centerLon',
        'faradayRotation',
        'product_file_id',
        'fileName',
        'flightDirection',
        'frameNumber',
        'groupID',
        'granuleType',
        'insarGrouping',
        'instrument',
        'md5sum',
        'offNadirAngle',
        'absoluteOrbit',
        'relativeOrbit',
        'platform',
        'pointingAngle',
        'polarization',
        'processingDate',
        'processingLevel',
        'granuleName',
        'sensor',
        'shape',
        'startTime',
        'stopTime',
        'downloadUrl'
    ]
    return fields

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
                'beamMode': p['beamMode'],
                'beamModeType': p['beamModeType'],
                'browse': p['browse'],
                'bytes': p['bytes'],
                'centerLat': p['centerLat'],
                'centerLon': p['centerLon'],
                'faradayRotation': p['faradayRotation'],
                'fileID': p['product_file_id'],
                'fileName': p['fileName'],
                'flightDirection': p['flightDirection'],
                'frameNumber': p['frameNumber'],
                'groupID': p['groupID'],
                'granuleType': p['granuleType'],
                'insarStackId': p['insarGrouping'],
                'instrument': p['instrument'],
                'md5sum': p['md5sum'],
                'offNadirAngle': p['offNadirAngle'],
                'orbit': p['absoluteOrbit'][0],
                'pathNumber': p['relativeOrbit'],
                'platform': p['platform'],
                'pointingAngle': p['pointingAngle'],
                'polarization': p['polarization'],
                'processingDate': p['processingDate'],
                'processingLevel': p['processingLevel'],
                'sceneName': p['granuleName'],
                'sensor': p['sensor'],
                'startTime': p['startTime'],
                'stopTime': p['stopTime'],
                'url': p['downloadUrl']
            }
        }
        if self.includeBaseline:
            result['properties']['temporalBaseline'] = p['temporalBaseline']
            result['properties']['perpendicularBaseline'] = p['perpendicularBaseline']

        return result
