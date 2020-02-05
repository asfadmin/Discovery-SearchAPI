import logging
from lxml import etree as ET


def parse_cmr_response(r):
    """
    Convert echo10 xml to results list used by output translators
    """
    logging.debug('parsing CMR results')

    try:
        root = ET.fromstring(r.text.encode('latin-1'))
    except ET.ParseError as e:
        logging.error(f'CMR parsing error: {e} when parsing: {r.text}')
        return

    num_results = len(root.xpath('/results/result/Granule'))
    logging.debug(f'Found {num_results} results in this page')

    for granule in root.xpath('/results/result/Granule'):
        yield parse_granule(granule)


def parse_granule(granule):
    (shape, wkt_shape) = wkt_from_gpolygon(
        granule.xpath('./Spatial/HorizontalSpatialDomain/Geometry/GPolygon')
    )

    def get_val(path, default=None):
        r = granule.xpath(path)

        if r is not None and len(r) > 0:
            return r[0].text
        else:
            return default

    frame_number = get_val(attr('FRAME_NUMBER'), default='NA') \
        if get_val(attr('ASF_PLATFORM'), default='NA') in ['Sentinel-1A', 'Sentinel-1B', 'ALOS'] \
        else get_val(attr('CENTER_ESA_FRAME'), default='NA')

    result = {
        'granuleName': get_val("./DataGranule/ProducerGranuleId"),
        'sizeMB': get_val("./DataGranule/SizeMBDataGranule"),
        'processingDate':  get_val("./DataGranule/ProductionDateTime"),
        'startTime':  get_val("./Temporal/RangeDateTime/BeginningDateTime"),
        'stopTime':  get_val("./Temporal/RangeDateTime/EndingDateTime"),
        'absoluteOrbit': get_val(
            "./OrbitCalculatedSpatialDomains/OrbitCalculatedSpatialDomain/OrbitNumber"),
        'platform': get_val(attr('ASF_PLATFORM'), default=get_val("./Platforms/Platform/ShortName")),
        'md5sum': get_val(attr('MD5SUM'), default='NA'),
        'beamMode': get_val(attr('BEAM_MODE_TYPE'), default='NA'),
        'configurationName': get_val(attr('BEAM_MODE_DESC'), default='NA'),
        'bytes': get_val(attr("BYTES"), default='NA'),
        'granuleType':  get_val(attr('GRANULE_TYPE'), default='NA'),
        'sceneDate': get_val(attr('ACQUISITION_DATE'), default='NA'),
        'flightDirection': get_val(attr('ASCENDING_DESCENDING'), default='NA'),
        'thumbnailUrl': get_val(attr('THUMBNAIL_URL'), default='NA'),
        'farEndLat':  get_val(attr('FAR_END_LAT'), default='NA'),
        'farStartLat':  get_val(attr('FAR_START_LAT'), default='NA'),
        'nearStartLat':  get_val(attr('NEAR_START_LAT'), default='NA'),
        'nearEndLat':  get_val(attr('NEAR_END_LAT'), default='NA'),
        'farEndLon':  get_val(attr('FAR_END_LON'), default='NA'),
        'farStartLon':  get_val(attr('FAR_START_LON'), default='NA'),
        'nearStartLon':  get_val(attr('NEAR_START_LON'), default='NA'),
        'nearEndLon':  get_val(attr('NEAR_END_LON'), default='NA'),
        'processingType':  get_val(attr('PROCESSING_LEVEL'), default='NA'),
        'finalFrame':  get_val(attr('CENTER_ESA_FRAME'), default='NA'),
        'centerLat':  get_val(attr('CENTER_LAT'), default='NA'),
        'centerLon':  get_val(attr('CENTER_LON'), default='NA'),
        'polarization':  get_val(attr('POLARIZATION'), default='NA'),
        'faradayRotation':  get_val(attr('FARADAY_ROTATION'), default='NA'),
        'stringFootprint': wkt_shape,
        'doppler': get_val(attr('DOPPLER'), default='NA'),
        'baselinePerp': get_val(attr('INSAR_BASELINE'), default='NA'),
        'insarStackSize': get_val(attr('INSAR_STACK_SIZE'), default='NA'),
        'processingDescription': get_val(attr('PROCESSING_DESCRIPTION'), default='NA'),
        'percentTroposphere': 'NA', # not in CMR
        'frameNumber': frame_number,
        'percentCoherence': 'NA', # not in CMR
        'productName': get_val("./DataGranule/ProducerGranuleId"),
        'masterGranule': 'NA', # almost always None in API
        'percentUnwrapped': 'NA', # not in CMR
        'beamSwath': 'NA', # .......complicated
        'insarGrouping': get_val(attr('INSAR_STACK_ID'), default='NA'),
        'offNadirAngle': get_val(attr('OFF_NADIR_ANGLE'), default='NA'),
        'missionName': get_val(attr('MISSION_NAME'), default='NA'),
        'relativeOrbit': get_val(attr('PATH_NUMBER'), default='NA'),
        'flightLine': get_val(attr('FLIGHT_LINE'), default='NA'),
        'processingTypeDisplay': get_val(attr('PROCESSING_TYPE_DISPLAY'), default='NA'),
        'track': get_val(attr('PATH_NUMBER'), default='NA'),
        'beamModeType': get_val(attr('BEAM_MODE_TYPE'), default='NA'),
        'processingLevel': get_val(attr('PROCESSING_TYPE'), default='NA'),
        'lookDirection': get_val(attr('LOOK_DIRECTION'), default='NA'),
        'varianceTroposphere': 'NA', # not in CMR
        'slaveGranule': 'NA', # almost always None in API
        'sensor': get_val('./Platforms/Platform/Instruments/Instrument/ShortName'),
        'fileName': get_val("./OnlineAccessURLs/OnlineAccessURL/URL").split('/')[-1],
        'downloadUrl': get_val("./OnlineAccessURLs/OnlineAccessURL/URL"),
        'browse': get_browse_urls(granule.xpath('./AssociatedBrowseImageUrls')),
        'shape': shape,
        'sarSceneId': 'NA', # always None in API
        'product_file_id': get_val("./GranuleUR"),
        'sceneId': get_val("./DataGranule/ProducerGranuleId"),
        'firstFrame': get_val(attr('CENTER_ESA_FRAME'), default='NA'),
        'frequency': 'NA', # always None in API
        'catSceneId': 'NA', # always None in API
        'status': 'NA', # always None in API
        'formatName': 'NA', # always None in API
        'incidenceAngle': 'NA', # always None in API
        'collectionName': get_val(attr('MISSION_NAME'), default='NA'),
        'sceneDateString': 'NA', # always None in API
        'groupID': get_val(attr('GROUP_ID'), default='NA'),
    }

    for k in result:
        if result[k] == 'NULL':
            result[k] = None

    return result


def attr(name):
    """
    Convenience method for handling echo10 additional attributes
    """
    return (
        "./AdditionalAttributes/AdditionalAttribute"
        f"[Name='{name}']/Values/Value"
    )


def wkt_from_gpolygon(gpoly):
    """
    for kml generation
    """
    shapes = []
    for g in gpoly:
        shapes.append([])
        for point in g.iter('Point'):
            shapes[-1].append({
                'lon': point.findtext('PointLongitude'),
                'lat': point.findtext('PointLatitude')
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


def get_browse_urls(browseElems):
    browseList = []

    for b in browseElems:
        browseList.extend(b.findall('ProviderBrowseUrl'))

    browseUrls = [''.join(b.itertext()).strip() for b in browseList]
    browseUrls.sort()

    return browseUrls
