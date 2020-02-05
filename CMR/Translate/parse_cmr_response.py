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

    def get_val(path, default='NA'):
        r = granule.xpath(path)

        if r is not None and len(r) > 0:
            return r[0].text
        else:
            return default

    def get_attr(path, default='NA'):
        return get_val(attr(path), default=default)

    asf_platforms = ['Sentinel-1A', 'Sentinel-1B', 'ALOS']
    frame_number = get_attr('FRAME_NUMBER') \
        if get_attr('ASF_PLATFORM') in asf_platforms \
        else get_attr('CENTER_ESA_FRAME')

    result = {
        'granuleName': get_val("./DataGranule/ProducerGranuleId", default=None),
        'sizeMB': get_val("./DataGranule/SizeMBDataGranule", default=None),
        'processingDate':  get_val("./DataGranule/ProductionDateTime", default=None),
        'startTime':  get_val("./Temporal/RangeDateTime/BeginningDateTime", default=None),
        'stopTime':  get_val("./Temporal/RangeDateTime/EndingDateTime", default=None),
        'absoluteOrbit': get_val(
            "./OrbitCalculatedSpatialDomains/OrbitCalculatedSpatialDomain/OrbitNumber",
            default=None
        ),
        'platform': get_attr(
            'ASF_PLATFORM',
            default=get_val("./Platforms/Platform/ShortName")
        ),
        'md5sum': get_attr('MD5SUM'),
        'beamMode': get_attr('BEAM_MODE_TYPE'),
        'configurationName': get_attr('BEAM_MODE_DESC'),
        'bytes': get_attr("BYTES"),
        'granuleType':  get_attr('GRANULE_TYPE'),
        'sceneDate': get_attr('ACQUISITION_DATE'),
        'flightDirection': get_attr('ASCENDING_DESCENDING'),
        'thumbnailUrl': get_attr('THUMBNAIL_URL'),
        'farEndLat':  get_attr('FAR_END_LAT'),
        'farStartLat':  get_attr('FAR_START_LAT'),
        'nearStartLat':  get_attr('NEAR_START_LAT'),
        'nearEndLat':  get_attr('NEAR_END_LAT'),
        'farEndLon':  get_attr('FAR_END_LON'),
        'farStartLon':  get_attr('FAR_START_LON'),
        'nearStartLon':  get_attr('NEAR_START_LON'),
        'nearEndLon':  get_attr('NEAR_END_LON'),
        'processingType':  get_attr('PROCESSING_LEVEL'),
        'finalFrame':  get_attr('CENTER_ESA_FRAME'),
        'centerLat':  get_attr('CENTER_LAT'),
        'centerLon':  get_attr('CENTER_LON'),
        'polarization':  get_attr('POLARIZATION'),
        'faradayRotation':  get_attr('FARADAY_ROTATION'),
        'stringFootprint': wkt_shape,
        'doppler': get_attr('DOPPLER'),
        'baselinePerp': get_attr('INSAR_BASELINE'),
        'insarStackSize': get_attr('INSAR_STACK_SIZE'),
        'processingDescription': get_attr('PROCESSING_DESCRIPTION'),
        'percentTroposphere': 'NA',  # not in CMR
        'frameNumber': frame_number,
        'percentCoherence': 'NA',  # not in CMR
        'productName': get_val("./DataGranule/ProducerGranuleId", default=None),
        'masterGranule': 'NA',  # almost always None in API
        'percentUnwrapped': 'NA',  # not in CMR
        'beamSwath': 'NA',  # .......complicated
        'insarGrouping': get_attr('INSAR_STACK_ID'),
        'offNadirAngle': get_attr('OFF_NADIR_ANGLE'),
        'missionName': get_attr('MISSION_NAME'),
        'relativeOrbit': get_attr('PATH_NUMBER'),
        'flightLine': get_attr('FLIGHT_LINE'),
        'processingTypeDisplay': get_attr('PROCESSING_TYPE_DISPLAY'),
        'track': get_attr('PATH_NUMBER'),
        'beamModeType': get_attr('BEAM_MODE_TYPE'),
        'processingLevel': get_attr('PROCESSING_TYPE'),
        'lookDirection': get_attr('LOOK_DIRECTION'),
        'varianceTroposphere': 'NA',  # not in CMR
        'slaveGranule': 'NA',  # almost always None in API
        'sensor': get_val('./Platforms/Platform/Instruments/Instrument/ShortName', default=None),
        'fileName': get_val("./OnlineAccessURLs/OnlineAccessURL/URL", default=None).split('/')[-1],
        'downloadUrl': get_val("./OnlineAccessURLs/OnlineAccessURL/URL", default=None),
        'browse': get_browse_urls(granule, './AssociatedBrowseImageUrls'),
        'shape': shape,
        'sarSceneId': 'NA',  # always None in API
        'product_file_id': get_val("./GranuleUR", default=None),
        'sceneId': get_val("./DataGranule/ProducerGranuleId", default=None),
        'firstFrame': get_attr('CENTER_ESA_FRAME'),
        'frequency': 'NA',  # always None in API
        'catSceneId': 'NA',  # always None in API
        'status': 'NA',  # always None in API
        'formatName': 'NA',  # always None in API
        'incidenceAngle': 'NA',  # always None in API
        'collectionName': get_attr('MISSION_NAME'),
        'sceneDateString': 'NA',  # always None in API
        'groupID': get_attr('GROUP_ID'),
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


def get_browse_urls(granule, browse_path):
    browse_elems = granule.xpath(browse_path)
    browseList = []

    for b in browse_elems:
        browseList.extend(b.findall('ProviderBrowseUrl'))

    browseUrls = [''.join(b.itertext()).strip() for b in browseList]
    browseUrls.sort()

    return browseUrls
