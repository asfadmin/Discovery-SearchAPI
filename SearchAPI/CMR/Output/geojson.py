import logging
import json
from .json import JSONStreamArray

def req_fields_geojson():
    fields = [
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
        'downloadUrl',
        'stateVectors'
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
                'url': p['downloadUrl'],
                'baseline': {
                    'stateVectors': {
                        'positions': {
                            'prePosition': p['sv_pos_pre'],
                            'postPosition': p['sv_pos_post'],
                            'prePositionTime': p['sv_t_pos_pre'],
                            'postPositionTime': p['sv_t_pos_post']
                        },
                        'velocities': {
                            'preVelocity': p['sv_vel_pre'],
                            'postVelocity': p['sv_vel_post'],
                            'preVelocityTime': p['sv_t_vel_pre'],
                            'postVelocityTime': p['sv_t_vel_post']
                        }
                    }
                    
                },
                # 'temporalBaseline': p.pop('temporalBaseline'),
                # 'perpendicularBaseline': p.pop('perpendicularBaseline')
            }
        }
        # if self.includeBaseline:
        # result['properties']['temporalBaseline'] = p.pop('temporalBaseline')
        # result['properties']['perpendicularBaseline'] = p.pop('perpendicularBaseline')

        return result
