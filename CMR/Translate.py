#import defusedxml.ElementTree as ET
#import xml.etree.cElementTree as ET
from lxml import etree as ET
import dateparser
from datetime import datetime
import requests
import logging
from asf_env import get_config
from CMR.Input import parse_int, parse_float, parse_string, parse_wkt, parse_date
from CMR.Input import parse_string_list, parse_int_or_range_list, parse_float_or_range_list
from CMR.Input import parse_coord_string, parse_bbox_string, parse_point_string
from CMR.Output import output_translators

def fix_polygon(v):
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
            logging.debug('Backwards polygon, attempting to repair')
            logging.debug(r.text)
            it = iter(v)
            rev = reversed(list(zip(it, it)))
            rv = [i for sub in rev for i in sub]
            r = requests.post(get_config()['cmr_api'], data={'polygon': ','.join(rv), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
            if r.status_code == 200:
                logging.debug('Polygon repaired')
                v = rv
            else:
                logging.warning('Polygon repair needed but reversing the points did not help, query will fail')
    return ','.join(v)

# A few inputs need to be specially handled to make the flexible input the legacy
# API allowed match what's at CMR, since we can't use wildcards on additional attributes
def input_fixer(params):
    fixed_params = {}
    for k in params:
        v = params[k]
        k = k.lower()
        if k == 'lookdirection': # Vaguely wildcard-like behavior
            if v[0].upper() not in ['L', 'R']:
                raise ValueError('Invalid look direction: {0}'.format(v))
            fixed_params[k] = v[0].upper()
        elif k == 'flightdirection': # Vaguely wildcard-like behavior
            if v[0].upper() not in ['A', 'D']:
                raise ValueError('Invalid flight direction: {0}'.format(v))
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
        elif k == 'beammode':
            beammap = {
                'STD': 'Standard'
            }
            fixed_params[k] = [beammap[a.upper()] if a.upper() in beammap else a for a in v]
        elif k == 'beamswath':
            beammap = {
                'STANDARD': 'STD'
            }
            fixed_params[k] = [beammap[a.upper()] if a.upper() in beammap else a for a in v]
        elif k == 'polygon': # Do what we can to fix polygons up
            fixed_params[k] = fix_polygon(v)
        elif k == 'intersectswith': # Need to take the parsed value here and send it to one of polygon=, line=, point=
            (t, p) = v.split(':')
            if t == 'polygon':
                p = fix_polygon(p)
            fixed_params[t] = p
        else:
            fixed_params[k] = v

    # set default start and end dates if needed, and then make sure they're formatted correctly
    # whether using the default or not
    start_s = fixed_params['start'] if 'start' in fixed_params else '1978-01-01T00:00:00Z'
    end_s = fixed_params['end'] if 'end' in fixed_params else datetime.utcnow().isoformat()
    start = dateparser.parse(start_s, settings={'RETURN_AS_TIMEZONE_AWARE': True})
    end = dateparser.parse(end_s, settings={'RETURN_AS_TIMEZONE_AWARE': True})

    # Check/fix the order of start/end
    if start > end:
        start, end = end, start
    # Final temporal string that will actually be used
    fixed_params['temporal'] = '{0},{1}'.format(start.strftime('%Y-%m-%dT%H:%M:%SZ'), end.strftime('%Y-%m-%dT%H:%M:%SZ'))
    # And a little cleanup
    fixed_params.pop('start', None)
    fixed_params.pop('end', None)

    return fixed_params

# Supported input parameters and their associated CMR parameters
def input_map():
    return {
#       API parameter           CMR parameter               CMR format strings                  Parser
        'output':               [None,                      '{0}',                              parse_string],
        'maxresults':           [None,                      '{0}',                              parse_int],
        'absoluteorbit':        ['orbit_number',            '{0}',                              parse_int_or_range_list],
        'asfframe':             ['attribute[]',             'int,FRAME_NUMBER,{0}',             parse_int_or_range_list],
        'maxbaselineperp':      ['attribute[]',             'float,INSAR_BASELINE,,{0}',        parse_float],
        'minbaselineperp':      ['attribute[]',             'float,INSAR_BASELINE,{0},',        parse_float],
        'beammode':             ['attribute[]',             'string,BEAM_MODE,{0}',             parse_string_list],
        'beamswath':            ['attribute[]',             'string,BEAM_MODE_TYPE,{0}',        parse_string_list],
        'collectionname':       ['attribute[]',             'string,MISSION_NAME,{0}',          parse_string_list],
        'maxdoppler':           ['attribute[]',             'float,DOPPLER,,{0}',               parse_float],
        'mindoppler':           ['attribute[]',             'float,DOPPLER,{0},',               parse_float],
        'maxfaradayrotation':   ['attribute[]',             'float,FARADAY_ROTATION,,{0}',      parse_float],
        'minfaradayrotation':   ['attribute[]',             'float,FARADAY_ROTATION,{0},',      parse_float],
        'flightdirection':      ['attribute[]',             'string,ASCENDING_DESCENDING,{0}',  parse_string],
        'flightline':           ['attribute[]',             'string,FLIGHT_LINE,{0}',           parse_string],
        'frame':                ['attribute[]',             'int,CENTER_ESA_FRAME,{0}',         parse_int_or_range_list],
        'granule_list':         ['readable_granule_name[]', '{0}',                              parse_string_list],
        'product_list':         ['granule_ur[]',            '{0}',                              parse_string_list],
        'maxinsarstacksize':    ['attribute[]',             'int,INSAR_STACK_SIZE,,{0}',        parse_int],
        'mininsarstacksize':    ['attribute[]',             'int,INSAR_STACK_SIZE,{0},',        parse_int],
        'intersectswith':       [None,                      '{0}',                              parse_wkt],
        'lookdirection':        ['attribute[]',             'string,LOOK_DIRECTION,{0}',        parse_string],
        'offnadirangle':        ['attribute[]',             'float,OFF_NADIR_ANGLE,{0}',        parse_float_or_range_list],
        'platform':             ['attribute[]',             'string,ASF_PLATFORM,{0}',          parse_string_list],
        'polarization':         ['attribute[]',             'string,POLARIZATION,{0}',          parse_string_list],
        'polygon':              ['polygon',                 '{0}',                              parse_coord_string], # intersectsWith ends up here
        'linestring':           ['line',                    '{0}',                              parse_coord_string], # or here
        'point':                ['point',                   '{0}',                              parse_point_string], # or here
        'bbox':                 ['bounding_box',            '{0}',                              parse_bbox_string],
        'processinglevel':      ['attribute[]',             'string,PROCESSING_TYPE,{0}',       parse_string_list],
        'relativeorbit':        ['attribute[]',             'int,PATH_NUMBER,{0}',              parse_int_or_range_list],
        'processingdate':       ['attribute[]',             'date,PROCESSING_DATE,{0},',        parse_date],
        'start':                [None,                      '{0}',                              parse_date],
        'end':                  [None,                      '{0}',                              parse_date],
        'temporal':             ['temporal',                '{0}',                              None], # start/end end up here
        'groupid':              ['attribute[]',             'string,GROUP_ID,{0}',              parse_string_list]
    }

# translate supported params into CMR params
def translate_params(p):
    params = {}

    for k in p:
        if k.lower() not in input_map():
            raise ValueError('Unsupported CMR parameter', k)
        try:
            params[k.lower()] = input_map()[k.lower()][2](p[k])
        except ValueError as e:
            raise e

    # be nice to make this not a special case
    output = 'metalink'
    if 'output' in params and params['output'].lower() in output_translators():
        output = params['output'].lower()
    if 'output' in params:
        del params['output']
    max_results = None
    if 'maxresults' in params:
        max_results = params['maxresults']
        if max_results < 1:
            raise ValueError('Invalid maxResults, must be > 0: {0}'.format(max_results))
        del params['maxresults']
    return params, output, max_results

# convenience method for handling echo10 additional attributes
def attr(name):
    return "./AdditionalAttributes/AdditionalAttribute/[Name='" + name + "']/Values/Value"

# for kml generation
def wkt_from_gpolygon(gpoly):
    shapes = []
    for g in gpoly:
        shapes.append([])
        for point in g.iter('Point'):
            shapes[-1].append({'lon': point.findtext('PointLongitude'), 'lat': point.findtext('PointLatitude')})
        if shapes[-1][0]['lat'] != shapes[-1][-1]['lat'] or shapes[-1][0]['lon'] != shapes[-1][-1]['lon']:
            shapes[-1].append(shapes[-1][0]) # Close the shape if needed
    longest = shapes[0]
    for shape in shapes:
        if len(shape) > len(longest):
            longest = shape
    wkt_shape = 'POLYGON(({0}))'.format(','.join(['{0} {1}'.format(x['lon'], x['lat']) for x in longest]))
    #logging.debug('Translated to WKT: {0}'.format(wkt))
    return longest, wkt_shape

# Convert echo10 xml to results list used by output translators
def parse_cmr_response(r):
    logging.debug('parsing CMR results')
    try:
        root = ET.fromstring(r.text.encode('latin-1'))
    except ET.ParseError as e:
        logging.error('CMR parsing error: {0} when parsing: {1}'.format(e, r.text))
        return
    for granule in root.iterfind('./result/Granule'):
        (shape, wkt_shape) = wkt_from_gpolygon(granule.findall('./Spatial/HorizontalSpatialDomain/Geometry/GPolygon'))
        result = {
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
            'frameNumber': (granule.findtext(attr('FRAME_NUMBER'), default='NA') if granule.findtext(attr('ASF_PLATFORM'), default='NA') in ['Sentinel-1A', 'Sentinel-1B', 'ALOS'] else granule.findtext(attr('CENTER_ESA_FRAME'), default='NA')),
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
            #'product_file_id': '{0}_{1}'.format(granule.findtext("./DataGranule/ProducerGranuleId"), granule.findtext(attr('PROCESSING_TYPE'))),
            'product_file_id': granule.findtext("./GranuleUR"),
            'sceneId': granule.findtext("./DataGranule/ProducerGranuleId"),
            'firstFrame': granule.findtext(attr('CENTER_ESA_FRAME'), default='NA'),
            'frequency': 'NA', # always None in API
            'catSceneId': 'NA', # always None in API
            'status': 'NA', # always None in API
            'formatName': 'NA', # always None in API
            'incidenceAngle': 'NA', # always None in API
            'collectionName': granule.findtext(attr('MISSION_NAME'), default='NA'),
            'sceneDateString': 'NA', # always None in API
            'groupID': granule.findtext(attr('GROUP_ID'), default='NA'),
        }
        for k in result:
            if result[k] == 'NULL':
                result[k] = None
        yield result
