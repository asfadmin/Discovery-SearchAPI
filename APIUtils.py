import logging
from CMR.Input import parse_wkt
from geomet import wkt
from asf_env import get_config
import requests
import shapely.wkt

def repairWKT(wkt_str):
    repairs = []

    # Check the syntax and type
    try:
        wkt_obj = wkt.loads(wkt_str)
        if wkt_obj['type'].upper() not in ['POINT', 'LINESTRING', 'POLYGON']:
            shape = shapely.wkt.loads(wkt.dumps(wkt_obj)).convex_hull
            if shape.geom_type.upper() not in ['POINT', 'LINESTRING', 'POLYGON']:
                raise TypeError('Invalid WKT type ({0}): must be Point, LineString, or Polygon'.format(wkt_obj['type']))
            else:
                wkt_obj = wkt.loads(shape.wkt)
                repairs.append({
                    'type': 'CONVEX_HULL',
                    'report': 'Shape was not a point, linestring, or polygon; using the convex hull instead'
                })
    except ValueError as e:
        return { 'error': {'type': 'VALUE', 'report': 'Could not parse WKT: {0}'.format(str(e))} }
    except TypeError as e:
        return { 'error': {'type': 'TYPE', 'report': str(e)} }


    if wkt_obj['type'] == 'Polygon': # only use the outer perimeter
        coords = wkt_obj['coordinates'][0]
    elif wkt_obj['type'] == 'Point':
        coords = [wkt_obj['coordinates']]
    else:
        coords = wkt_obj['coordinates']

    # Clamp coords to +/-90 and wrap to +/-180
    wrapped = 0
    clamped = 0
    for idx, itm in enumerate(coords):
        if abs(((coords[idx][0] + 180) % 360 - 180) - coords[idx][0]) > 0.000001:
            coords[idx][0] = ((coords[idx][0] + 180) % 360 - 180)
            wrapped += 1
        if coords[idx][1] != sorted((-90, coords[idx][1], 90))[1]:
            coords[idx][1] = sorted((-90, coords[idx][1], 90))[1]
            clamped += 1
    if wrapped > 0:
        repairs.append({
            'type': 'WRAP',
            'report': 'Wrapped {0} values to +/-180 longitude'.format(wrapped)
        })
        logging.debug(repairs[-1])
    if clamped > 0:
        repairs.append({
            'type': 'CLAMP',
            'report': 'Clamped {0} values to +/-90 latitude'.format(wrapped)
        })
        logging.debug(repairs[-1])

    # Check for polygon-specific issues
    if wkt_obj['type'] == 'Polygon':
        if coords[0][0] != coords[-1][0] or coords[0][1] != coords[-1][1]:
            coords.append(coords[0])
            repairs.append({
                'type': 'CLOSE',
                'report': 'Closed open polygon'
            })
            logging.debug(repairs[-1])

    # Re-assemble the repaired object
    if wkt_obj['type'] == 'Polygon':
        wkt_obj['coordinates'] = [coords]
    elif wkt_obj['type'] == 'Point':
        wkt_obj['coordinates'] = coords[0]
    else:
        wkt_obj['coordinates'] = coords

    def shape_len(shp):
        shp_type = shp.geom_type.upper()
        if shp_type == 'POINT':
            return 1
        if shp_type == 'LINESTRING':
            return len(shp.coords)
        if shp_type == 'POLYGON':
            return len(shp.exterior.coords)
        return None

    # Do some shapely magic
    original_shape = shapely.wkt.loads(wkt.dumps(wkt_obj))
    tolerance = 0.00001
    attempts = 1
    shape = original_shape.simplify(tolerance, preserve_topology=True)
    while shape_len(shape) > 300 and attempts <= 10:
        attempts += 1
        logging.debug('Shape length still {0}, simplifying further with tolerance {1}'.format(shape_len(shape), tolerance * 5))
        tolerance *= 5
        shape = original_shape.simplify(tolerance, preserve_topology=True)
    if attempts > 10:
        return { 'error': {'type': 'SIMPLIFY', 'report': 'Could not simplify shape after {0} iterations'.format(attempts)} }
    if shape_len(original_shape) != shape_len(shape):
        repairs.append({
            'type': 'SIMPLIFY',
            'report': 'Simplified shape from {0} points to {1} points'.format(shape_len(original_shape), shape_len(shape))
        })
        logging.debug(repairs[-1])

    wkt_obj = wkt.loads(shapely.wkt.dumps(shape))

    if wkt_obj['type'] == 'Polygon':
        # Check polygons for winding order or any CMR-related issues
        cmr_coords = parse_wkt(wkt.dumps(wkt_obj)).split(':')[1].split(',')
        repair = False
        cfg = get_config()
        r = requests.post(cfg['cmr_base'] + cfg['cmr_api'], headers=cfg['cmr_headers'], data={'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1})
        logging.debug({'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
        if r.status_code != 200:
            if 'Please check the order of your points.' in r.text:
                it = iter(cmr_coords)
                rev = reversed(list(zip(it, it)))
                rv = [i for sub in rev for i in sub]
                r = requests.post(cfg['cmr_base'] + cfg['cmr_api'], headers=cfg['cmr_headers'], data={'polygon': ','.join(rv), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
                if r.status_code == 200:
                    repair = True
                else:
                    return { 'error': {'type': 'UNKNOWN', 'report': 'Tried to repair winding order but still getting CMR error: {0}'.format(r.text)} }
            elif 'The polygon boundary intersected itself' in r.text:
                return { 'error': {'type': 'SELF_INTERSECT', 'report': 'Self-intersecting polygon'}}
            else:
                return { 'error': {'type': 'UNKNOWN', 'report': 'Unknown CMR error: {0}'.format(r.text)}}
        if repair:
            repairs.append({'type': 'REVERSE', 'report': 'Reversed polygon winding order'})
            logging.debug(repairs[-1])
            wkt_obj['coordinates'][0].reverse()

    # All done
    return {
        'wkt': wkt.dumps(wkt_obj),
        'repairs': repairs
    }
