import xml.etree.ElementTree as ET
from datetime import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
import logging
import json
import requests
import urls

templateEnv = Environment(
    loader=PackageLoader('CMR', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Parsers/validators
def input_parsers():
    return {
        'output': parse_string,
        'maxresults': parse_int,
        'granule_list': parse_string_list,
        'polygon': parse_coord_string
    }

# Supported input parameters
def input_map():
    return {
        'output': 'output',
        'maxresults': 'maxresults',
        'granule_list': 'readable_granule_name[]',
        'polygon': 'polygon'
    }

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
    
# translate supported params into CMR params
def translate_params(p):
    params = {}
    
    for k in p.keys():
        if k.lower() not in input_map().keys():
            raise ValueError('Unsupported CMR parameter', k)
        try:
            params[input_map()[k.lower()]] = input_parsers()[k.lower()](p[k])
        except ValueError as e:
            raise e
    
    # be nice to make this not a special case
    output = 'metalink'
    if 'output' in params and params['output'] in output_translators().keys():
        output = params['output']
        del params['output']
    max_results = None
    if 'maxresults' in params:
        max_results = params['maxresults']
        del params['maxresults']
    return params, output, max_results

def parse_string(v):
    return '{0}'.format(v)

def parse_string_list(v):
    return ['{0}'.format(a) for a in v.split(',')]

def parse_int(v):
    try:
        return int(v)
    except ValueError:
        raise ValueError('Invalid int: {0}'.format(v))

def parse_float(v):
    try:
        return float(v)
    except ValueError:
        raise ValueError('Invalid number: {0}'.format(v))

def parse_coord_string(v):
    coords = v.replace(' ', '').split(',')
    # if the polygon doesn't wrap, fix that
    if coords[0] != coords[-2] or coords[1] != coords[-1]:
        coords.extend(coords[0:2])
    for c in coords:
        try:
            float(c)
        except ValueError:
            raise ValueError('Invalid polygon: {0}'.format(v))
    return ','.join(coords)

# for kml generation
def wkt_from_gpolygon(gpoly):
    shape = []
    for point in gpoly.iter('Point'):
        shape.append({'lon': point.findtext('PointLongitude'), 'lat': point.findtext('PointLatitude')})
    wkt = 'POLYGON(({0}))'.format(','.join(list(map(lambda x: '{0} {1}'.format(x['lon'], x['lat']), shape))))
    #logging.debug('Translated to WKT: {0}'.format(wkt))
    return shape, wkt

# convenience method for handling echo10 additional attributes
def attr(name):
    return "./AdditionalAttributes/AdditionalAttribute/[Name='" + name + "']/Values/Value"

# Convert echo10 xml to results list used by output translators
def parse_cmr_response(r):
    logging.debug('parsing results to list')
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError as e:
        logging.error('CMR parsing error: {0} when parsing: {1}'.format(e, r.text))
        return []
    results = []
    for result in root.iter('result'):
        for granule in result.iter('Granule'):
            (shape, wkt) = wkt_from_gpolygon(granule.find('./Spatial/HorizontalSpatialDomain/Geometry/GPolygon'))
            results.append({
                'granuleName': granule.findtext("./DataGranule/ProducerGranuleId"),
                'sizeMB': granule.findtext("./DataGranule/SizeMBDataGranule"),
                'processingDate':  granule.findtext("./DataGranule/ProductionDateTime"),
                'startTime':  granule.findtext("./Temporal/RangeDateTime/BeginningDateTime"),
                'stopTime':  granule.findtext("./Temporal/RangeDateTime/EndingDateTime"),
                'absoluteOrbit': granule.findtext("./OrbitCalculatedSpatialDomains/OrbitCalculatedSpatialDomain/OrbitNumber"),
                'platform': granule.findtext(attr('ASF_PLATFORM')),
                'md5': granule.findtext(attr('MD5SUM')),
                'beamMode': granule.findtext(attr('BEAM_MODE_TYPE')),
                'configurationName': granule.findtext(attr('BEAM_MODE_DESC')),
                'bytes': granule.findtext(attr("BYTES")),
                'granuleType':  granule.findtext(attr('GRANULE_TYPE')),
                'sceneDate': granule.findtext(attr('ACQUISITION_DATE')),
                'flightDirection': granule.findtext(attr('ASCENDING_DESCENDING')),
                'thumbnailUrl': granule.findtext(attr('THUMBNAIL_URL')),
                'farEndLat':  granule.findtext(attr('FAR_END_LAT')),
                'farStartLat':  granule.findtext(attr('FAR_START_LAT')),
                'nearStartLat':  granule.findtext(attr('NEAR_START_LAT')),
                'nearEndLat':  granule.findtext(attr('NEAR_END_LAT')),
                'farEndLon':  granule.findtext(attr('FAR_END_LON')),
                'farStartLon':  granule.findtext(attr('FAR_START_LON')),
                'nearStartLon':  granule.findtext(attr('NEAR_START_LON')),
                'nearEndLon':  granule.findtext(attr('NEAR_END_LON')),
                'processingType':  granule.findtext(attr('PROCESSING_LEVEL')),
                'finalFrame':  granule.findtext(attr('CENTER_ESA_FRAME')),
                'centerLat':  granule.findtext(attr('CENTER_LAT')),
                'centerLon':  granule.findtext(attr('CENTER_LON')),
                'polarization':  granule.findtext(attr('POLARIZATION')),
                'faradayRotation':  granule.findtext(attr('FARADAY_ROTATION')),
                'stringFootprint': wkt,
                'doppler': granule.findtext(attr('DOPPLER')),
                'baselinePerp': granule.findtext(attr('INSAR_BASELINE')),
                'insarStackSize': granule.findtext(attr('INSAR_STACK_SIZE')),
                'processingDescription': granule.findtext(attr('PROCESSING_DESCRIPTION')),
                'percentTroposphere': None, # not in CMR
                'frameNumber': granule.findtext(attr('FRAME_NUMBER')),
                'percentCoherence': None, # not in CMR
                'productName': granule.findtext("./DataGranule/ProducerGranuleId"),
                'masterGranule': None, # almost always None in API
                'percentUnwrapped': None, # not in CMR
                'beamSwath': None, # .......complicated
                'insarGrouping': granule.findtext(attr('INSAR_STACK_ID')),
                'offNadirAngle': granule.findtext(attr('OFF_NADIR_ANGLE')),
                'missionName': granule.findtext(attr('MISSION_NAME')),
                'relativeOrbit': granule.findtext(attr('PATH_NUMBER')),
                'flightLine': granule.findtext(attr('FLIGHT_LINE')),
                'processingTypeDisplay': granule.findtext(attr('PROCESSING_TYPE_DISPLAY')),
                'track': granule.findtext(attr('PATH_NUMBER')),
                'beamModeType': granule.findtext(attr('BEAM_MODE_TYPE')),
                'processingLevel': granule.findtext(attr('PROCESSING_TYPE')),
                'lookDirection': granule.findtext(attr('LOOK_DIRECTION')),
                'varianceTroposphere': None, # not in CMR
                'slaveGranule': None, # almost always None in API
                'sensor': granule.findtext('./Platforms/Platform/Instruments/Instrument/ShortName'),
                'fileName': granule.findtext("./OnlineAccessURLs/OnlineAccessURL/URL").split('/')[-1],
                'downloadUrl': granule.findtext("./OnlineAccessURLs/OnlineAccessURL/URL"),
                'browse': granule.findtext("./AssociatedBrowseImageUrls/ProviderBrowseUrl/URL"),
                'shape': shape,
                'sarSceneId': None, # always None in API
                'product_file_id': '{0}_{1}'.format(granule.findtext("./DataGranule/ProducerGranuleId"), granule.findtext(attr('PROCESSING_TYPE'))),
                'sceneId': granule.findtext("./DataGranule/ProducerGranuleId"),
                'firstFrame': granule.findtext(attr('CENTER_ESA_FRAME')),
                'frequency': None, # always None in API
                'catSceneId': None, # always None in API
                'status': None, # always None in API
                'formatName': None, # always None in API
                'incidenceAngle': None, # always None in API
                'collectionName': granule.findtext(attr('MISSION_NAME')),
                'sceneDateString': None # always None in API
            })

    # some additional attributes are specified as "NULL", make it real null
    for r in results:
        for k in r.keys():
            if r[k] == 'NULL':
                r[k] = None
    return results

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
        'slaveGranule'
    ]
    json_data = [[]]
    # just grab the parts of the data we want to match legacy API json output
    for p in products['results']:
        json_data[0].append(dict((k, p[k]) for k in legacy_json_keys if k in p))
    return json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ':'))

def cmr_to_download(rlist):
    logging.debug('translating: bulk download script')
    bd_res = requests.post(urls.bulk_download_api, data={'products': ','.join([p['downloadUrl'] for p in rlist])})
    return (bd_res.text)

def finalize_echo10(response):
    logging.debug('translating: echo10 passthrough')
    # eventually this will consolidate multiple echo10 files
    return response.text
