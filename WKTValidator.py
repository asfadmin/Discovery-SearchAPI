from flask import Response
import logging
import json
from CMR.Translate import fix_polygon
from CMR.Input import parse_wkt
from geomet import wkt
import requests
from asf_env import get_config

class WKTValidator:

    def __init__(self, request):
        self.request = request  # store the incoming request
        if 'wkt' in self.request.values:
            self.wkt = self.request.values['wkt'].upper()
        else:
            self.wkt = None

    def get_response(self):
        repairs = []
        parsed = None
        # Check the syntax and type
        try:
            wkt_obj = wkt.loads(self.wkt)
            if wkt_obj['type'] not in ['Point', 'LineString', 'Polygon']:
                raise TypeError('Invalid WKT type ({0}): must be Point, LineString, or Polygon'.format(wkt_obj['type']))
        except ValueError as e:
            result = { 'error': 'Could not parse WKT: {0}'.format(str(e)) }
            return Response(json.dumps(result), 200)
        except TypeError as e:
            result = { 'error': str(e) }
            return Response(json.dumps(result), 200)


        if wkt_obj['type'] == 'Polygon': # only use the outer perimeter
            logging.debug('doing this one')
            coords = wkt_obj['coordinates'][0]
        elif wkt_obj['type'] == 'Point':
            coords = [wkt_obj['coordinates']]
        else:
            coords = wkt_obj['coordinates']

        # Round each coordinate
        rounded = 0
        for idx, itm in enumerate(coords):
            if coords[idx][0] != round(itm[0], 6):
                rounded += 1
            if coords[idx][1] != round(itm[1], 6):
                rounded += 1
            coords[idx][0] = round(itm[0], 6)
            coords[idx][1] = round(itm[1], 6)
        if rounded > 0:
            repairs.append({'type': 'ROUND', 'report': 'Rounded {0} coordinate values'.format(rounded)})

        # Check for duplicates
        new_coords = [coords[0]]
        trimmed = -1 # Because the first point is pre-populated
        for c in coords:
            if c[0] != new_coords[-1][0] or c[1] != new_coords[-1][1]:
                new_coords.append(c)
            else:
                trimmed += 1
        coords = new_coords
        if trimmed > 0:
            repairs.append({'type': 'TRIM', 'report': 'Trimmed {0} duplicate coordinates'.format(trimmed)})

        # Check for polygon-specific issues
        if wkt_obj['type'] == 'Polygon':
            if coords[0][0] != coords[-1][0] or coords[0][1] != coords[-1][1]:
                coords.append(coords[0])
                repairs.append({'type': 'CLOSURE', 'report': 'Closed open polygon'})

        # Re-assemble the repaired object
        if wkt_obj['type'] == 'Polygon':
            wkt_obj['coordinates'] = [coords]
        elif wkt_obj['type'] == 'Point':
            wkt_obj['coordinates'] = coords[0]
        else:
            wkt_obj['coordinates'] = coords

        if wkt_obj['type'] == 'Polygon':
            # Check polygons for winding order or any CMR-related issues
            cmr_coords = parse_wkt(wkt.dumps(wkt_obj)).split(':')[1].split(',')
            repair = False
            r = requests.post(get_config()['cmr_api'], data={'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1})
            if r.status_code != 200:
                if 'Please check the order of your points.' in r.text:
                    it = iter(cmr_coords)
                    rev = reversed(list(zip(it, it)))
                    rv = [i for sub in rev for i in sub]
                    r = requests.post(get_config()['cmr_api'], data={'polygon': ','.join(rv), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
                    if r.status_code == 200:
                        repair = True
                    else:
                        result = { 'error': 'Tried to repair winding order but still getting CMR error: {0}'.format(r.text) }
                        return Response(json.dumps(result), 200)
                elif 'The polygon boundary intersected itself':
                    result = { 'error': 'Self-intersecting polygon'}
                    return Response(json.dumps(result), 200)
                else:
                    result = { 'error': 'Unknown CMR error: {0}'.format(r.text)}
                    return Response(json.dumps(result), 200)
            if repair:
                repairs.append({'type': 'REVERSED', 'report': 'Reversed polygon winding order'})
                wkt_obj['coordinates'][0].reverse()

        # All done
        result = {
            'wkt': wkt.dumps(wkt_obj, decimals=6),
            'repairs': repairs
        }
        return Response(json.dumps(result), 200)
