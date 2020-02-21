import logging
import json
from functools import reduce
import dateparser

def parse_cmr_response(r):
    """
    Convert umm json to results list used by output translators
    """
    logging.debug('parsing CMR results')

    try:
        results = json.loads(r.text.encode('latin-1'))
    except json.JSONDecodeError as e:
        logging.error(f'CMR parsing error: {e} when parsing: {r.text}')
        return
    num_results = len(results.get('items', 0))
    logging.debug(f'Found {num_results} results in this page')

    for granule in results.get('items'):
        yield parse_granule(granule['umm'])


def parse_granule(granule):
    # Build a dict out of the list of attributes
    def list_to_dict(list, key, path):
        attributes = {}
        for attr in list:
            attributes[attr[key]] = get_val(attr, path)
        return attributes

    # Special case handling for some properties/groups

    attributes = list_to_dict(get_val(granule, 'AdditionalAttributes'), key='Name', path='Values/[0]')

    processing_dates = sorted(get_val(granule, 'ProviderDates'), \
        reverse=True, \
        key=lambda x: \
            dateparser.parse(x['Date']) if x['Type'] in ['Insert', 'Update'] \
            else None)
    data_granule_identifiers = list_to_dict(get_val(granule, 'DataGranule/Identifiers'), key='IdentifierType', path='Identifier')
    product_urls = [url['URL'] for url in get_val(granule, 'RelatedUrls') if url['Type'] == 'GET DATA']
    browse_urls = [url['URL'] for url in get_val(granule, 'RelatedUrls') if url['Type'] == 'GET RELATED VISUALIZATION']
    shape, wkt_shape = wkt_from_gpolygon(
        get_val(granule, 'SpatialExtent/HorizontalSpatialDomain/Geometry/GPolygons')
    )
    frame_number = attributes.get('FRAME_NUMBER') \
        if attributes.get('ASF_PLATFORM') in ['Sentinel-1A', 'Sentinel-1B', 'ALOS'] \
        else attributes.get('CENTER_ESA_FRAME')

    result = {
        'granuleName':              data_granule_identifiers['ProducerGranuleId'],
        'sizeMB':                   get_val(granule, 'DataGranule/ArchiveAndDistributionInformation/[0]/Size'),
        'processingDate':           get_val(granule, "ProcessingDates/[0]"),
        'startTime':                get_val(granule, "TemporalExtent/RangeDateTime/BeginningDateTime"),
        'stopTime':                 get_val(granule, "TemporalExtent/RangeDateTime/EndingDateTime"),
        'absoluteOrbit':            get_val(granule, "OrbitCalculatedSpatialDomains/[0]/OrbitNumber"),
        'platform':                 attributes.get(
                                        'ASF_PLATFORM',
                                        get_val(granule, "Platforms/[0]/ShortName")
                                    ),
        'md5sum':                   attributes.get('MD5SUM'),
        'beamMode':                 attributes.get('BEAM_MODE_TYPE'),
        'configurationName':        attributes.get('BEAM_MODE_DESC'),
        'bytes':                    attributes.get('BYTES'),
        'granuleType':              attributes.get('GRANULE_TYPE'),
        'sceneDate':                attributes.get('ACQUISITION_DATE'),
        'flightDirection':          attributes.get('ASCENDING_DESCENDING'),
        'thumbnailUrl':             attributes.get('THUMBNAIL_URL'),
        'farEndLat':                attributes.get('FAR_END_LAT'),
        'farStartLat':              attributes.get('FAR_START_LAT'),
        'nearStartLat':             attributes.get('NEAR_START_LAT'),
        'nearEndLat':               attributes.get('NEAR_END_LAT'),
        'farEndLon':                attributes.get('FAR_END_LON'),
        'farStartLon':              attributes.get('FAR_START_LON'),
        'nearStartLon':             attributes.get('NEAR_START_LON'),
        'nearEndLon':               attributes.get('NEAR_END_LON'),
        'processingType':           attributes.get('PROCESSING_LEVEL'),
        'finalFrame':               attributes.get('CENTER_ESA_FRAME'),
        'centerLat':                attributes.get('CENTER_LAT'),
        'centerLon':                attributes.get('CENTER_LON'),
        'polarization':             attributes.get('POLARIZATION'),
        'faradayRotation':          attributes.get('FARADAY_ROTATION'),
        'stringFootprint':          wkt_shape,
        'doppler':                  attributes.get('DOPPLER'),
        'baselinePerp':             attributes.get('INSAR_BASELINE'),
        'insarStackSize':           attributes.get('INSAR_STACK_SIZE'),
        'processingDescription':    attributes.get('PROCESSING_DESCRIPTION'),
        'percentTroposphere':       None,  # not in CMR
        'frameNumber':              frame_number,
        'percentCoherence':         None,  # not in CMR
        'productName':              data_granule_identifiers['ProducerGranuleId'],
        'masterGranule':            None,  # no longer populated in CMR
        'percentUnwrapped':         None,  # not in CMR
        'beamSwath':                None,  # .......complicated
        'insarGrouping':            attributes.get('INSAR_STACK_ID'),
        'offNadirAngle':            attributes.get('OFF_NADIR_ANGLE'),
        'missionName':              attributes.get('MISSION_NAME'),
        'relativeOrbit':            attributes.get('PATH_NUMBER'),
        'flightLine':               attributes.get('FLIGHT_LINE'),
        'processingTypeDisplay':    attributes.get('PROCESSING_TYPE_DISPLAY'),
        'track':                    attributes.get('PATH_NUMBER'),
        'beamModeType':             attributes.get('BEAM_MODE_TYPE'),
        'processingLevel':          attributes.get('PROCESSING_TYPE'),
        'lookDirection':            attributes.get('LOOK_DIRECTION'),
        'varianceTroposphere':      None,  # not in CMR
        'slaveGranule':             None,  # no longer populated in CMR
        'sensor':                   get_val(granule, 'Platforms/[0]/Instruments/[0]/ShortName'),
        'fileName':                 product_urls[0].split('/')[-1] if len(product_urls) > 0 else None,
        'downloadUrl':              product_urls[0] if len(product_urls) > 0 else None,
        'browse':                   browse_urls if len(browse_urls) > 0 else [],
        'shape':                    shape,
        'sarSceneId':               None,  # always None in API
        'product_file_id':          get_val(granule, 'GranuleUR'),
        'sceneId':                  data_granule_identifiers['ProducerGranuleId'],
        'firstFrame':               attributes.get('CENTER_ESA_FRAME'),
        'frequency':                None,  # always None in API
        'catSceneId':               None,  # always None in API
        'status':                   None,  # always None in API
        'formatName':               None,  # always None in API
        'incidenceAngle':           None,  # always None in API
        'collectionName':           attributes.get('MISSION_NAME'),
        'sceneDateString':          None,  # always None in API
        'groupID':                  attributes.get('GROUP_ID'),
    }

    for k in result:
        if result[k] == 'NULL':
            result[k] = None

    return result

def get_val(dictionary, keys, default=None):
    """
    For picking out directly-locatable properties using an xmlpath-like approach with defaults along the way
    """
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else d[int(key.strip('[]'))] if isinstance(d, list) else default, keys.split("/"), dictionary)


def wkt_from_gpolygon(gpoly):
    """
    for kml generation
    """
    shapes = []
    for g in gpoly:
        shapes.append([])
        for point in get_val(g, 'Boundary/Points'):
            shapes[-1].append({
                'lon': point.get('Longitude', 0.0), # Use a default that'll still "work"
                'lat': point.get('Latitude', 0.0)
            })

        if shape_not_closed(shapes):
            # Close the shape if needed
            shapes[-1].append(shapes[-1][0])

    longest = shapes[0]
    for shape in shapes:
        if len(shape) > len(longest):
            longest = shape

    wkt_shape = 'POLYGON(({0}))'.format(
        ','.join(['{0} {1}'.format(x['lon'], x['lat']) for x in longest])
    )

    return longest, wkt_shape


def shape_not_closed(shapes):
    return (
        shapes[-1][0]['lat'] != shapes[-1][-1]['lat'] or
        shapes[-1][0]['lon'] != shapes[-1][-1]['lon']
    )


def get_browse_urls(granule, browse_path):
    browse_elems = granule.xpath(browse_path)
    browseList = []

    for b in browse_elems:
        browseList.extend(b.findall('ProviderBrowseUrl'))

    browseUrls = [''.join(b.itertext()).strip() for b in browseList]
    browseUrls.sort()

    return browseUrls
