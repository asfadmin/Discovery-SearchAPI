import logging
from jinja2 import Environment, PackageLoader
import json
import requests
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
        'count':        [count, 'text/plain; charset=utf-8', 'txt'],
        'download':     [cmr_to_download, 'text/plain; charset=utf-8', 'py']
    }

def count(r):
    logging.debug('translating: count')
    return str(r)

def cmr_to_metalink(rgen):
    logging.debug('translating: metalink')
    template = templateEnv.get_template('metalink.tmpl')
    for l in template.stream(results=rgen()):
        yield l

def cmr_to_csv(rgen):
    logging.debug('translating: csv')
    template = templateEnv.get_template('csv.tmpl')
    for l in template.stream(results=rgen()):
        yield l

def cmr_to_download(rgen):
    logging.debug('translating: bulk download script')
    plist = [p['downloadUrl'] for p in rgen()]
    bd_res = requests.post(get_config()['bulk_download_api'], data={'products': ','.join(plist)})
    yield (bd_res.text)

def cmr_to_kml(rgen):
    logging.debug('translating: kml')
    template = templateEnv.get_template('kml.tmpl')
    for l in template.stream(results=rgen()):
        yield l

def cmr_to_json(rgen):
    logging.debug('translating: json')

    streamer = JSONStreamArray(rgen)
    
    for p in json.JSONEncoder().iterencode([streamer]):
        yield p

class JSONStreamArray(list):
    def __init__(self, gen):
        self.gen = gen
        
    def __iter__(self):
        return self.gen()

    def __len__(self):
        return 1
    
    def streamDicts(self):
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
            'sizeMB'
        ]
        for p in self.gen():
            yield dict((k, p[k]) for k in legacy_json_keys if k in p)
