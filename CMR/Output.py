import logging
from datetime import datetime
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
        'metalink':     cmr_to_metalink,
        'csv':          cmr_to_csv,
        'kml':          cmr_to_kml,
        'json':         cmr_to_json,
        'count':        None, # No translator, just here for input validation
        'echo10':       finalize_echo10,
        'download':     cmr_to_download
    }

def cmr_to_metalink(rlist):
    logging.debug('translating: metalink')
    products = {'results': rlist}
    template = templateEnv.get_template('metalink.tmpl')
    return template.render(products)

def cmr_to_csv(rlist):
    logging.debug('translating: csv')
    products = {'results': rlist}
    template = templateEnv.get_template('csv.tmpl')
    return template.render(products)

def cmr_to_kml(rlist):
    logging.debug('translating: kml')
    products = {'results': rlist}
    template = templateEnv.get_template('kml.tmpl')
    return template.render(products, search_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))

def cmr_to_json(rlist):
    logging.debug('translating: json')
    products = {'results': rlist}
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
    json_data = [[]]
    # just grab the parts of the data we want to match legacy API json output
    for p in products['results']:
        json_data[0].append(dict((k, p[k]) for k in legacy_json_keys if k in p))
    return json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ':'))

def cmr_to_download(rlist):
    logging.debug('translating: bulk download script')
    bd_res = requests.post(get_config()['bulk_download_api'], data={'products': ','.join([p['downloadUrl'] for p in rlist])})
    return (bd_res.text)

def finalize_echo10(response):
    logging.debug('translating: echo10 passthrough')
    # eventually this will consolidate multiple echo10 files
    return response.text
