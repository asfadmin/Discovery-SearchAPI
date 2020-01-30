import logging
from jinja2 import Environment, PackageLoader
import json
import requests
from geomet import wkt
from asf_env import get_config

templateEnv = Environment(
    loader=PackageLoader('CMR', 'templates'),
    autoescape=True
)

# Supported output formats
def output_translators():
    return {
        'metalink':     [cmr_to_metalink, 'application/metalink+xml; charset=utf-8', 'metalink'],
        'csv':          [cmr_to_csv, 'text/csv; charset=utf-8', 'csv'],
        'kml':          [cmr_to_kml, 'application/vnd.google-earth.kml+xml; charset=utf-8', 'kmz'],
        'json':         [cmr_to_json, 'application/json; charset=utf-8', 'json'],
        'jsonlite':     [cmr_to_jsonlite, 'application/json; charset=utf-8', 'json'],
        'geojson':      [cmr_to_geojson, 'application/geojson; charset=utf-8', 'geojson'],
        'count':        [count, 'text/plain; charset=utf-8', 'txt'],
        'download':     [cmr_to_download, 'text/plain; charset=utf-8', 'py']
    }

def count(r):
    logging.debug('translating: count')
    return str(r)

def cmr_to_metalink(rgen):
    logging.debug('translating: metalink')
    template = templateEnv.get_template('template.metalink')
    for l in template.stream(results=rgen()):
        yield l

def cmr_to_csv(rgen):
    logging.debug('translating: csv')
    template = templateEnv.get_template('template.csv')
    for l in template.stream(results=rgen()):
        yield l

def cmr_to_kml(rgen):
    logging.debug('translating: kml')
    template = templateEnv.get_template('template.kml')
    for l in template.stream(results=rgen()):
        yield l

def cmr_to_download(rgen):
    logging.debug('translating: bulk download script')
    plist = [p['downloadUrl'] for p in rgen()]
    bd_res = requests.post(get_config()['bulk_download_api'], data={'products': ','.join(plist)})
    yield (bd_res.text)

def cmr_to_json(rgen):
    logging.debug('translating: json')

    streamer = JSONStreamArray(rgen)

    for p in json.JSONEncoder(indent=2, sort_keys=True).iterencode([streamer]):
        yield p

def cmr_to_jsonlite(rgen):
    logging.debug('translating: jsonlite')

    streamer = JSONLiteStreamArray(rgen)

    for p in json.JSONEncoder(sort_keys=True).iterencode({'results': streamer}):
        yield p

def cmr_to_geojson(rgen):
    logging.debug('translating: geojson')

    streamer = GeoJSONStreamArray(rgen)

    for p in json.JSONEncoder(indent=2, sort_keys=True).iterencode({'type': 'FeatureCollection','features':streamer}):
        yield p

# Some trickery is required to make JSONEncoder().iterencode take any ol' generator,
# this approach works without slurping the list into memory
class JSONStreamArray(list):
    def __init__(self, gen):
        self.gen = gen

        # need to make sure we actually have results so we can intelligently set __len__, otherwise
        # iterencode behaves strangely and will output invalid json
        self.first_result = None
        self.len = 0
        for p in self.gen():
            if p is not None:
                self.first_result = p
                self.len = 1
                break


    def __iter__(self):
        return self.streamDicts()

    def __len__(self):
        return self.len

    def streamDicts(self):
        for p in self.gen():
            if p is not None:
                yield self.getItem(p)

    # Override this method for other json-based output formats (i.e. geojson)
    def getItem(self, p):
        p['browse'] = p['browse'][0] if len(p['browse']) > 0 else None
        legacy_json_keys = [
            'sceneSize',
            'absoluteOrbit',
            'farEndLat',
            'sensor',
            'farStartLat',
            'processingTypeName',
            'finalFrame',
            'lookAngle',
            'processingType',
            'startTime',
            'stringFootprint',
            'doppler',
            'baselinePerp',
            'sarSceneId',
            'insarStackSize',
            'centerLat',
            'processingDescription',
            'product_file_id',
            'nearEndLon',
            'farEndLon',
            'percentTroposphere',
            'frameNumber',
            'percentCoherence',
            'nearStartLon',
            'sceneDate',
            'sceneId',
            'productName',
            'platform',
            'masterGranule',
            'thumbnailUrl',
            'percentUnwrapped',
            'beamSwath',
            'firstFrame',
            'insarGrouping',
            'centerLon',
            'faradayRotation',
            'fileName',
            'offNadirAngle',
            'granuleName',
            'frequency',
            'catSceneId',
            'farStartLon',
            'processingDate',
            'missionName',
            'relativeOrbit',
            'flightDirection',
            'granuleType',
            'configurationName',
            'polarization',
            'stopTime',
            'browse',
            'nearStartLat',
            'flightLine',
            'status',
            'formatName',
            'nearEndLat',
            'downloadUrl',
            'incidenceAngle',
            'processingTypeDisplay',
            'thumbnail',
            'track',
            'collectionName',
            'sceneDateString',
            'beamMode',
            'beamModeType',
            'processingLevel',
            'lookDirection',
            'varianceTroposphere',
            'slaveGranule',
            'sizeMB',
            'groupID',
            'md5sum'
        ]

        return dict((k, p[k]) for k in legacy_json_keys if k in p)

class JSONLiteStreamArray(JSONStreamArray):

    @staticmethod
    def getItem(p):
        for i in p.keys():
            if p[i] == 'NA' or p[i] == '':
                p[i] = None
        try:
            if float(p['offNadirAngle']) < 0:
                p['offNadirAngle'] = None
        except TypeError:
            pass

        try:
            if float(p['relativeOrbit']) < 0:
                p['relativeOrbit'] = None
        except TypeError:
            pass

        try:
            if p['groupID'] is None:
                p['groupID'] = p['granuleName']
        except TypeError:
            pass

        try:
            p['sizeMB'] = float(p['sizeMB'])
        except TypeError:
            pass

        try:
            p['relativeOrbit'] = int(p['relativeOrbit'])
        except TypeError:
            pass

        try:
            p['frameNumber'] = int(p['frameNumber'])
        except TypeError:
            pass

        try:
            p['absoluteOrbit'] = int(p['absoluteOrbit'])
        except TypeError:
            pass

        return {
            # Mandatory:
            'dataset': p['platform'],
            'downloadUrl': p['downloadUrl'],
            'fileName': p['fileName'],
            'granuleName': p['granuleName'],
            'groupID': p['groupID'],
            'productID': p['product_file_id'],
            'productType': p['processingLevel'],
            'productTypeDisplay': p['processingTypeDisplay'],
            'startTime': p['startTime'],
            'wkt': p['stringFootprint'],
            'wkt_unwrapped': unwrap_wkt(p['stringFootprint']),
            # Optional:
            'beamMode': p['beamMode'],
            'browse': p['browse'],
            'flightDirection': p['flightDirection'],
            'flightLine': p['flightLine'],
            'frame': p['frameNumber'],
            'missionName': p['missionName'],
            'orbit': p['absoluteOrbit'],
            'path': p['relativeOrbit'],
            'polarization': p['polarization'],
            'sizeMB': p['sizeMB'],
            'stackSize': p['insarStackSize'], # Used for datasets with precalculated stacks
            'thumb': p['thumbnailUrl'],
            # Dataset-specific:
            'faradayRotation': p['faradayRotation'], # ALOS
            'offNadirAngle': p['offNadirAngle'] # ALOS
        }

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

        return {
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



def unwrap_wkt(wkt_str):
    try:
        wkt_obj = wkt.loads(wkt_str)
        lons = [p[0] for p in wkt_obj['coordinates'][0]]
        if(max(lons) - min(lons) > 180):
            wkt_obj['coordinates'] = [[a if a[0] > 0 else [a[0] + 360, a[1]] for a in wkt_obj['coordinates'][0]]]
        return wkt.dumps(wkt_obj, decimals=6)
    except ValueError as e:
        return wkt_str
    return wkt_str
