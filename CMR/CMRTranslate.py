import xml.etree.ElementTree as ET
from datetime import datetime
import dateparser
import requests
from jinja2 import Environment, PackageLoader, select_autoescape
import logging
import json
import re
from geomet import wkt
from asf_env import get_config

templateEnv = Environment(
    loader=PackageLoader('CMR', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

# A few inputs need to be specially handled to make the flexible input the legacy
# API allowed match what's at CMR, since we can't use wildcards on additional attributes
def input_fixer(params):
    fixed_params = {}
    for k in params:
        v = params[k]
        k = k.lower()
        if k == 'lookdirection': # Vaguely wildcard-like behavior
            fixed_params[k] = v[0].upper()
        elif k == 'flightdirection': # Vaguely wildcard-like behavior
            fixed_params[k] = {'A': 'ASCENDING', 'D': 'DESCENDING'}[v[0].upper()]
        elif k == 'platform': # Legacy API allowed a few synonyms. If they're using one, translate it
            platmap = {
                'R1': 'RADARSAT-1',
                'E1': 'ERS-1',
                'E2': 'ERS-2',
                'J1': 'JERS-1',
                'A3': 'ALOS',
                'AS': 'AIRSAR',
                'SS': 'SEASAT',
                'SA': 'Sentinel-1A',
                'SB': 'Sentinel-1B',
                'SP': 'SMAP',
                'UA': 'UAVSAR'
            }
            fixed_params[k] = [platmap[a.upper()] if a.upper() in platmap else a for a in v]
        elif k == 'polygon': # Do what we can to fix polygons up
            # Trim whitespace and split it up
            v = v.replace(' ', '').split(',')
            
            # If the polygon doesn't wrap, fix that
            if v[0] != v[-2] or v[1] != v[-1]:
                v.extend(v[0:2])
            
            # Do a quick CMR query to see if the shape is wound correctly
            logging.debug('Checking winding order')
            r = requests.post(get_config()['cmr_api'], data={'polygon': ','.join(v), 'provider': 'ASF', 'page_size': 1})
            if r.status_code == 200:
                logging.debug('Winding order looks good')
            else:
                if 'Please check the order of your points.' in r.text:
                    logging.warning('Backwards polygon, attempting to repair')
                    logging.warning(r.text)
                    it = iter(v)
                    rev = reversed(zip(it, it))
                    rv = [i for sub in rev for i in sub]
                    r = requests.post(get_config()['cmr_api'], data={'polygon': ','.join(rv), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
                    if r.status_code == 200:
                        logging.warning('Polygon repaired')
                        v = rv
                    else:
                        logging.warning('Could not repair polygon, using original')
            fixed_params[k] = ','.join(v)        
        else:
            fixed_params[k] = v
    
    # set default start and end dates if needed, and then make sure they're formatted correctly
    # whether using the default or not
    if 'start' not in fixed_params:
        fixed_params['start'] = '1978-01-01T00:00:00Z'
    fixed_params['start'] = dateparser.parse(fixed_params['start']).strftime('%Y-%m-%dT%H:%M:%SZ')
    if 'end' not in fixed_params:
        fixed_params['end'] = 'now'
    fixed_params['end'] = dateparser.parse(fixed_params['end']).strftime('%Y-%m-%dT%H:%M:%SZ')
    # Final temporal string that will actually be used
    fixed_params['temporal'] = '{0},{1}'.format(fixed_params['start'], fixed_params['end'])
    # And a little cleanup
    del fixed_params['start']
    del fixed_params['end']
    
    return fixed_params

# Parsers/validators
def input_parsers():
    return {
        'absoluteorbit': parse_int_or_range_list,
        'asfframe': parse_int_or_range_list,
        'maxbaselineperp': parse_float,
        'minbaselineperp': parse_float,
        'beammode': parse_string_list,
        'collectionname': parse_string,
        'maxdoppler': parse_float,
        'mindoppler': parse_float,
        'maxfaradayrotation': parse_float,
        'minfaradayrotation': parse_float,
        'flightdirection': parse_string,
        'flightline': parse_string,
        'frame': parse_int_or_range_list,
        'granule_list': parse_string_list,
        'maxinsarstacksize': parse_int,
        'mininsarstacksize': parse_int,
        'intersectswith': parse_wkt,
        'lookdirection': parse_string,
        'offnadirangle': parse_float_or_range_list,
        'output': parse_string,
        'platform': parse_string_list,
        'polarization': parse_string_list,
        'polygon': parse_coord_string,
        'processinglevel': parse_string_list,
        'relativeorbit': parse_int_or_range_list,
        'maxresults': parse_int,
        'processingdate': parse_date,
        'start': parse_date,
        'end': parse_date
        
    }

# Supported input parameters and their associated CMR parameters
def input_map():
    return {
        'output': ['output', '{0}'], # Special case, does not actually forward to CMR
        'maxresults': ['maxresults', '{0}'], # Special case, does not actually forward to CMR
        'absoluteorbit': ['orbit_number', '{0}'],
        'asfframe': ['attribute[]', 'int,FRAME_NUMBER,{0}'],
        'maxbaselineperp': ['attribute[]', 'float,INSAR_BASELINE,,{0}'],
        'minbaselineperp': ['attribute[]', 'float,INSAR_BASELINE,{0},'],
        'beammode': ['attribute[]', 'string,BEAM_MODE_TYPE,{0}'],
#        'collectionname': ['attribute[]', 'string,MISSION_NAME,{0}'], # double check this source
        'maxdoppler': ['attribute[]', 'float,DOPPLER,,{0}'],
        'mindoppler': ['attribute[]', 'float,DOPPLER,{0},'],
        'maxfaradayrotation': ['attribute[]', 'float,FARADAY_ROTATION,,{0}'],
        'minfaradayrotation': ['attribute[]', 'float,FARADAY_ROTATION,{0},'],
        'flightdirection': ['attribute[]', 'string,ASCENDING_DESCENDING,{0}'],
        'flightline': ['attribute[]', 'string,FLIGHT_LINE,{0}'],
        'frame': ['attribute[]', 'int,CENTER_ESA_FRAME,{0}'],
        'granule_list': ['readable_granule_name[]', '{0}'],
        'maxinsarstacksize': ['attribute[]', 'int,INSAR_STACK_SIZE,{0},'],
        'mininsarstacksize': ['attribute[]', 'int,INSAR_STACK_SIZE,,{0}'],
        #'intersectswith': [???],
        'lookdirection': ['attribute[]', 'string,LOOK_DIRECTION,{0}'],
        'platform': ['attribute[]', 'string,ASF_PLATFORM,{0}'],
        'polarization': ['attribute[]', 'string,POLARIZATION,{0}'],
        'polygon': ['polygon', '{0}'],
        'processinglevel': ['attribute[]', 'string,PROCESSING_TYPE,{0}'],
        'relativeorbit': ['attribute[]', 'int,PATH_NUMBER,{0}'],
#        'processingdate': parse_date,
        'start': ['end', '{0}'], # Isn't actually used for querying CMR, just checking inputs
        'end': ['start', '{0}'], # Isn't actually used for querying CMR, just checking inputs
        'temporal': ['temporal', '{0}'] # start/end end up here
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
    
    for k in p:
        if k.lower() not in input_map():
            raise ValueError('Unsupported CMR parameter', k)
        try:
            params[k.lower()] = input_parsers()[k.lower()](p[k])
        except ValueError as e:
            raise e
    
    # be nice to make this not a special case
    output = 'metalink'
    if 'output' in params and params['output'].lower() in output_translators():
        output = params['output'].lower()
        del params['output']
    max_results = None
    if 'maxresults' in params:
        max_results = params['maxresults']
        del params['maxresults']
    return params, output, max_results

# Parse and validate a string: "abc"
def parse_string(v):
    return '{0}'.format(v)

# Parse and validate an int: "10"
def parse_int(v):
    try:
        return int(v)
    except ValueError:
        raise ValueError('Invalid int: {0}'.format(v))

# Parse and validate a float: "1.2"
def parse_float(v):
    try:
        return float(v)
    except ValueError:
        raise ValueError('Invalid number: {0}'.format(v))

# Parse and validate a data: "1991-10-01T00:00:00Z"
def parse_date(v):
    return dateparser.parse(v).strftime('%Y-%m-%dT%H:%M:%SZ')

# Parse and validate a numeric value range, using h() to validate each value: "3-5", "1.1-12.3"
def parse_range(v, h):
    v = v.replace(' ', '')
    m = re.search(r'^(-?\d+(\.\d*)?)-(-?\d+(\.\d*)?)$', v)
    try:
        a = [h(m.group(1)), h(m.group(3))]
        if a[0] > a[1]:
            raise ValueError()
    except ValueError:
        raise ValueError('Invalid range: {0}'.format(v))
    return a

# Parse and validate an integer range: "3-5"
def parse_int_range(v):
    return parse_range(v, parse_int)

# Parse and validate a float range: "1.1-12.3"
def parse_float_range(v):
    return parse_range(v, parse_float)

# Parse and validate a list of values, using h() to validate each value: "a,b,c", "1,2,3", "1.1,2.3"
def parse_list(v, h):
    return [h(a) for a in v.split(',')]

# Parse and validate a list of strings: "foo,bar,baz"
def parse_string_list(v):
    return parse_list(v, '{0}'.format)

# Parse and validate a list of integers: "1,2,3"
def parse_int_list(v):
    return parse_list(v, parse_int)

# Parse and validate a list of floats: "1.1,2.3,4.5"
def parse_float_list(v):
    return parse_list(v, parse_float)

# Parse and validate a number or a range, using h() to validate each value: "1", "4.5", "3-5", "10.1-13.4"
def parse_number_or_range(v, h):
    m = re.search(r'^(-?\d+(\.\d*)?)$', v)
    if m is not None:
        return h(v)
    return parse_range(v, h)
    
# Parse and validate a list of numbers or number ranges, using h() to validate each value: "1,2,3-5", "1.1,1.4,5.1-6.7"
def parse_number_or_range_list(v, h):
    v = v.replace(' ', '')
    return [parse_number_or_range(x, h) for x in v.split(',')]

# Parse and validate a list of integers or integer ranges: "1,2,3-5"
def parse_int_or_range_list(v):
    return parse_number_or_range_list(v, parse_int)

# Parse and validate a list of integers or integer ranges: "1,2,3-5"
def parse_float_or_range_list(v):
    return parse_number_or_range_list(v, parse_float)

# Parse and validate a coordinate string
def parse_coord_string(v):
    v = v.split(',')
    for c in v:
        try:
            float(c)
        except ValueError:
            raise ValueError('Invalid polygon: {0}'.format(v))
    return ','.join(v)

# Parse a WKT and convert it to a coordinate string
def parse_wkt(v):
    if re.match(r'line|point|polygon', v.lower()) is None:
        raise ValueError('Unsupported WKT: {0}'.format(v))
    p = wkt.loads(v.upper())['coordinates'][0] # ignore any subsequent parts like holes, they aren't supported by CMR
    return ','.join([i for sub in p['coordinates'] for i in sub])

# for kml generation
def wkt_from_gpolygon(gpoly):
    shape = []
    for point in gpoly.iter('Point'):
        shape.append({'lon': point.findtext('PointLongitude'), 'lat': point.findtext('PointLatitude')})
    wkt_shape = 'POLYGON(({0}))'.format(','.join(list(map(lambda x: '{0} {1}'.format(x['lon'], x['lat']), shape))))
    #logging.debug('Translated to WKT: {0}'.format(wkt))
    return shape, wkt_shape

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
            (shape, wkt_shape) = wkt_from_gpolygon(granule.find('./Spatial/HorizontalSpatialDomain/Geometry/GPolygon'))
            results.append({
                'granuleName': granule.findtext("./DataGranule/ProducerGranuleId"),
                'sizeMB': granule.findtext("./DataGranule/SizeMBDataGranule"),
                'processingDate':  granule.findtext("./DataGranule/ProductionDateTime"),
                'startTime':  granule.findtext("./Temporal/RangeDateTime/BeginningDateTime"),
                'stopTime':  granule.findtext("./Temporal/RangeDateTime/EndingDateTime"),
                'absoluteOrbit': granule.findtext("./OrbitCalculatedSpatialDomains/OrbitCalculatedSpatialDomain/OrbitNumber"),
                'platform': granule.findtext(attr('ASF_PLATFORM'), default='NA'),
                'md5': granule.findtext(attr('MD5SUM'), default='NA'),
                'beamMode': granule.findtext(attr('BEAM_MODE_TYPE'), default='NA'),
                'configurationName': granule.findtext(attr('BEAM_MODE_DESC'), default='NA'),
                'bytes': granule.findtext(attr("BYTES"), default='NA'),
                'granuleType':  granule.findtext(attr('GRANULE_TYPE'), default='NA'),
                'sceneDate': granule.findtext(attr('ACQUISITION_DATE'), default='NA'),
                'flightDirection': granule.findtext(attr('ASCENDING_DESCENDING'), default='NA'),
                'thumbnailUrl': granule.findtext(attr('THUMBNAIL_URL'), default='NA'),
                'farEndLat':  granule.findtext(attr('FAR_END_LAT'), default='NA'),
                'farStartLat':  granule.findtext(attr('FAR_START_LAT'), default='NA'),
                'nearStartLat':  granule.findtext(attr('NEAR_START_LAT'), default='NA'),
                'nearEndLat':  granule.findtext(attr('NEAR_END_LAT'), default='NA'),
                'farEndLon':  granule.findtext(attr('FAR_END_LON'), default='NA'),
                'farStartLon':  granule.findtext(attr('FAR_START_LON'), default='NA'),
                'nearStartLon':  granule.findtext(attr('NEAR_START_LON'), default='NA'),
                'nearEndLon':  granule.findtext(attr('NEAR_END_LON'), default='NA'),
                'processingType':  granule.findtext(attr('PROCESSING_LEVEL'), default='NA'),
                'finalFrame':  granule.findtext(attr('CENTER_ESA_FRAME'), default='NA'),
                'centerLat':  granule.findtext(attr('CENTER_LAT'), default='NA'),
                'centerLon':  granule.findtext(attr('CENTER_LON'), default='NA'),
                'polarization':  granule.findtext(attr('POLARIZATION'), default='NA'),
                'faradayRotation':  granule.findtext(attr('FARADAY_ROTATION'), default='NA'),
                'stringFootprint': wkt_shape,
                'doppler': granule.findtext(attr('DOPPLER'), default='NA'),
                'baselinePerp': granule.findtext(attr('INSAR_BASELINE'), default='NA'),
                'insarStackSize': granule.findtext(attr('INSAR_STACK_SIZE'), default='NA'),
                'processingDescription': granule.findtext(attr('PROCESSING_DESCRIPTION'), default='NA'),
                'percentTroposphere': 'NA', # not in CMR
                'frameNumber': granule.findtext(attr('FRAME_NUMBER'), default='NA'),
                'percentCoherence': 'NA', # not in CMR
                'productName': granule.findtext("./DataGranule/ProducerGranuleId"),
                'masterGranule': 'NA', # almost always None in API
                'percentUnwrapped': 'NA', # not in CMR
                'beamSwath': 'NA', # .......complicated
                'insarGrouping': granule.findtext(attr('INSAR_STACK_ID'), default='NA'),
                'offNadirAngle': granule.findtext(attr('OFF_NADIR_ANGLE'), default='NA'),
                'missionName': granule.findtext(attr('MISSION_NAME'), default='NA'),
                'relativeOrbit': granule.findtext(attr('PATH_NUMBER'), default='NA'),
                'flightLine': granule.findtext(attr('FLIGHT_LINE'), default='NA'),
                'processingTypeDisplay': granule.findtext(attr('PROCESSING_TYPE_DISPLAY'), default='NA'),
                'track': granule.findtext(attr('PATH_NUMBER'), default='NA'),
                'beamModeType': granule.findtext(attr('BEAM_MODE_TYPE'), default='NA'),
                'processingLevel': granule.findtext(attr('PROCESSING_TYPE'), default='NA'),
                'lookDirection': granule.findtext(attr('LOOK_DIRECTION'), default='NA'),
                'varianceTroposphere': 'NA', # not in CMR
                'slaveGranule': 'NA', # almost always None in API
                'sensor': granule.findtext('./Platforms/Platform/Instruments/Instrument/ShortName'),
                'fileName': granule.findtext("./OnlineAccessURLs/OnlineAccessURL/URL").split('/')[-1],
                'downloadUrl': granule.findtext("./OnlineAccessURLs/OnlineAccessURL/URL"),
                'browse': granule.findtext("./AssociatedBrowseImageUrls/ProviderBrowseUrl/URL"),
                'shape': shape,
                'sarSceneId': 'NA', # always None in API
                'product_file_id': '{0}_{1}'.format(granule.findtext("./DataGranule/ProducerGranuleId"), granule.findtext(attr('PROCESSING_TYPE'))),
                'sceneId': granule.findtext("./DataGranule/ProducerGranuleId"),
                'firstFrame': granule.findtext(attr('CENTER_ESA_FRAME'), default='NA'),
                'frequency': 'NA', # always None in API
                'catSceneId': 'NA', # always None in API
                'status': 'NA', # always None in API
                'formatName': 'NA', # always None in API
                'incidenceAngle': 'NA', # always None in API
                'collectionName': granule.findtext(attr('MISSION_NAME'), default='NA'),
                'sceneDateString': 'NA' # always None in API
            })

    # some additional attributes are specified as "NULL", make it real null
    for r in results:
        for k in r:
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
    bd_res = requests.post(get_config()['bulk_download_api'], data={'products': ','.join([p['downloadUrl'] for p in rlist])})
    return (bd_res.text)

def finalize_echo10(response):
    logging.debug('translating: echo10 passthrough')
    # eventually this will consolidate multiple echo10 files
    return response.text
