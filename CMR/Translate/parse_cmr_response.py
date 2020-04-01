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
    def get_val(path, default='NA'):
        r = granule.xpath(path)

        if r is not None and len(r) > 0:
            return r[0].text
        else:
            return default

    def get_attr(path, default='NA'):
        return get_val(attr(path), default=default)

    shape, wkt_shape = wkt_from_gpolygon(
        granule.xpath('./Spatial/HorizontalSpatialDomain/Geometry/GPolygon')
    )

    asf_platforms = ['Sentinel-1A', 'Sentinel-1B', 'ALOS']
    frame_number = get_attr('FRAME_NUMBER') \
        if get_attr('ASF_PLATFORM') in asf_platforms \
        else get_attr('CENTER_ESA_FRAME')

    result = {
        'absoluteOrbit': get_val(
            "./OrbitCalculatedSpatialDomains/OrbitCalculatedSpatialDomain/OrbitNumber",
            default=None
        ),
        'baselinePerp': get_attr('INSAR_BASELINE'),
        'beamMode': get_attr('BEAM_MODE_TYPE'),
        'beamModeType': get_attr('BEAM_MODE_TYPE'),
        'beamSwath': 'NA',  # .......complicated
        'browse': get_browse_urls(granule, './AssociatedBrowseImageUrls'),
        'bytes': get_attr("BYTES"),
        'catSceneId': 'NA',  # always None in API
        'centerLat':  get_attr('CENTER_LAT'),
        'centerLon':  get_attr('CENTER_LON'),
        'collectionName': get_attr('MISSION_NAME'),
        'configurationName': get_attr('BEAM_MODE_DESC'),
        'doppler': get_attr('DOPPLER'),
        'downloadUrl': get_val("./OnlineAccessURLs/OnlineAccessURL/URL", default=None),
        'farEndLat':  get_attr('FAR_END_LAT'),
        'farEndLon':  get_attr('FAR_END_LON'),
        'farStartLat':  get_attr('FAR_START_LAT'),
        'farStartLon':  get_attr('FAR_START_LON'),
        'faradayRotation':  get_attr('FARADAY_ROTATION'),
        'fileName': get_val("./OnlineAccessURLs/OnlineAccessURL/URL", default=None).split('/')[-1],
        'finalFrame':  get_attr('CENTER_ESA_FRAME'),
        'firstFrame': get_attr('CENTER_ESA_FRAME'),
        'flightDirection': get_attr('ASCENDING_DESCENDING'),
        'flightLine': get_attr('FLIGHT_LINE'),
        'formatName': 'NA',  # always None in API
        'frameNumber': frame_number,
        'frequency': 'NA',  # always None in API
        'granuleName': get_val("./DataGranule/ProducerGranuleId", default=None),
        'granuleType':  get_attr('GRANULE_TYPE'),
        'groupID': get_attr('GROUP_ID'),
        'incidenceAngle': 'NA',  # always None in API
        'insarGrouping': get_attr('INSAR_STACK_ID'),
        'insarStackSize': get_attr('INSAR_STACK_SIZE'),
        'lookDirection': get_attr('LOOK_DIRECTION'),
        'masterGranule': 'NA',  # almost always None in API
        'md5sum': get_attr('MD5SUM'),
        'missionName': get_attr('MISSION_NAME'),
        'nearEndLat':  get_attr('NEAR_END_LAT'),
        'nearEndLon':  get_attr('NEAR_END_LON'),
        'nearStartLat':  get_attr('NEAR_START_LAT'),
        'nearStartLon':  get_attr('NEAR_START_LON'),
        'offNadirAngle': get_attr('OFF_NADIR_ANGLE'),
        'percentCoherence': 'NA',  # not in CMR
        'percentTroposphere': 'NA',  # not in CMR
        'percentUnwrapped': 'NA',  # not in CMR
        'platform': get_attr(
            'ASF_PLATFORM',
            default=get_val("./Platforms/Platform/ShortName")
        ),
        'polarization':  get_attr('POLARIZATION'),
        'processingDate':  get_val("./DataGranule/ProductionDateTime", default=None),
        'processingDescription': get_attr('PROCESSING_DESCRIPTION'),
        'processingLevel': get_attr('PROCESSING_TYPE'),
        'processingType':  get_attr('PROCESSING_LEVEL'),
        'processingTypeDisplay': get_attr('PROCESSING_TYPE_DISPLAY'),
        'productName': get_val("./DataGranule/ProducerGranuleId", default=None),
        'product_file_id': get_val("./GranuleUR", default=None),
        'relativeOrbit': get_attr('PATH_NUMBER'),
        'sarSceneId': 'NA',  # always None in API
        'sceneDate': get_attr('ACQUISITION_DATE'),
        'sceneDateString': 'NA',  # always None in API
        'sceneId': get_val("./DataGranule/ProducerGranuleId", default=None),
        'sensor': get_val('./Platforms/Platform/Instruments/Instrument/ShortName', default=None),
        'shape': shape,
        'sizeMB': get_val("./DataGranule/SizeMBDataGranule", default=None),
        'slaveGranule': 'NA',  # almost always None in API
        'startTime':  get_val("./Temporal/RangeDateTime/BeginningDateTime", default=None),
        'status': 'NA',  # always None in API
        'stopTime':  get_val("./Temporal/RangeDateTime/EndingDateTime", default=None),
        'stringFootprint': wkt_shape,
        'thumbnailUrl': get_attr('THUMBNAIL_URL'),
        'track': get_attr('PATH_NUMBER'),
        'varianceTroposphere': 'NA'  # not in CMR
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
