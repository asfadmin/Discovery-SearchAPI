import logging
from lxml import etree as ET
import datetime
from .fields import get_field_paths, attr_path


def parse_cmr_response(r, req_fields):
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
        yield parse_granule(granule, req_fields)


def parse_granule(granule, req_fields):
    req_fields = req_fields.copy() # gotta copy this list because we're gonna thrash it
    def get_val(path):
        r = granule.xpath(path)

        if r is not None and len(r) > 0:
            return r[0].text
        else:
            return None

    def remove_field(f):
        try:
            req_fields.remove(f)
        except ValueError:
            pass

    field_paths = get_field_paths()
    result = {}

    # Handle a few special cases
    if any(field in req_fields for field in ['shape', 'stringFootprint']):
        shape, wkt_shape = wkt_from_gpolygon(
            granule.xpath('./Spatial/HorizontalSpatialDomain/Geometry/GPolygon')
        )
        result['shape'] = shape
        result['stringFootprint'] = wkt_shape
        remove_field('shape')
        remove_field('stringFootprint')

    if any(field in req_fields for field in ['platform', 'frameNumber', 'canInsar']):
        platform = get_val(attr_path('ASF_PLATFORM'))
        if platform is None:
            platform = get_val('./Platforms/Platform/ShortName')
        result['platform'] = platform
        remove_field('platform')

    if 'frameNumber' in req_fields:
        asf_frame_platforms = ['Sentinel-1A', 'Sentinel-1B', 'ALOS']
        result['frameNumber'] = get_val(attr_path('FRAME_NUMBER')) \
            if result['platform'] in asf_frame_platforms \
            else get_val(attr_path('CENTER_ESA_FRAME'))
        remove_field('frameNumber')

    if 'browse' in req_fields:
        result['browse'] = get_browse_urls(granule, './AssociatedBrowseImageUrls')
        remove_field('browse')

    if 'fileName' in req_fields:
        result['fileName'] = get_val("./OnlineAccessURLs/OnlineAccessURL/URL").split('/')[-1]
        remove_field('fileName')

    if 'stateVectors' in req_fields or ('canInsar' in req_fields and result['platform'] not in ['ALOS', 'RADARSAT-1', 'JERS-1', 'ERS-1', 'ERS-2']):
        def parse_sv(sv):
            def float_or_none(a):
                try:
                    return float(a)
                except ValueError:
                    return None

            if sv is None:
                return (None, None)
            (x, y, z, t) = sv.split(',')
            v = [float_or_none(x), float_or_none(y), float_or_none(z)]
            if None not in v:
                return (v, t if datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%f') is not None else None)
            else:
                return (None, None)

        result['sv_pos_pre'],  result['sv_t_pos_pre']  = parse_sv(get_val(attr_path('SV_POSITION_PRE')))
        result['sv_pos_post'], result['sv_t_pos_post'] = parse_sv(get_val(attr_path('SV_POSITION_POST')))
        result['sv_vel_pre'],  result['sv_t_vel_pre']  = parse_sv(get_val(attr_path('SV_VELOCITY_PRE')))
        result['sv_vel_post'], result['sv_t_vel_post'] = parse_sv(get_val(attr_path('SV_VELOCITY_POST')))
        remove_field('stateVectors')

    if 'canInsar' in req_fields:
        if result['platform'] in ['ALOS', 'RADARSAT-1', 'JERS-1', 'ERS-1', 'ERS-2']:
            result['insarGrouping'] = get_val(field_paths['insarGrouping'])
            remove_field('insarGrouping')
            if result['insarGrouping'] not in [None, 0, '0', 'NA', 'NULL']:
                result['canInsar'] = True
        elif None not in [
            result['sv_pos_pre'], result['sv_pos_post'],
            result['sv_vel_pre'], result['sv_vel_post'],
            result['sv_t_pos_pre'], result['sv_t_pos_post'],
            result['sv_t_vel_pre'], result['sv_t_vel_post']]:
            result['canInsar'] = True
        else:
            result['canInsar'] = False
        remove_field('canInsar')

    # These fields are always None or NA and should be fully deprecated/removed in the future
    deprecated_fields = [
        'beamSwath',
        'catSceneId',
        'formatName',
        'frequency',
        'incidenceAngle',
        'masterGranule',
        'percentCoherence',
        'percentTroposphere',
        'percentUnwrapped',
        'sarSceneId',
        'sceneDateString',
        'slaveGranule',
        'status',
        'varianceTroposphere'
    ]
    for f in deprecated_fields:
        if f in req_fields:
            result[f] = None
            try:
                req_fields.remove(f)
            except ValueError:
                pass

    # Parse any remaining needed fields from the CMR response
    for field in req_fields:
        result[field] = get_val(field_paths[field])

    for k in result:
        if result[k] in ['NULL', 'NA', 'None']:
            result[k] = None

    return result


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
