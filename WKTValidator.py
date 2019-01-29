from flask import Response
import logging
import json
from CMR.Translate import fix_polygon
from CMR.Input import parse_wkt
from geomet import wkt

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
                raise ValueError('Invalid WKT type ({0}): must be Point, LineString, or Polygon'.format(wkt_obj['type']))
        except ValueError as e:
            result = { 'error': str(e) }
            return Response(json.dumps(result), 200)

        # Round each coordinate
        coords = wkt_obj['coordinates']
        rounded = 0
        for idx, itm in enumerate(coords):
            if coords[idx][0] != round(itm[0], 3):
                rounded += 1
            if coords[idx][1] != round(itm[1], 3):
                rounded += 1
            coords[idx][0] = round(itm[0], 3)
            coords[idx][1] = round(itm[1], 3)
        if rounded > 0:
            repairs.append('Rounded {0} coordinate values'.format(rounded))

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
            repairs.append('Trimmed {0} duplicate coordinates'.format(trimmed))

        wkt_obj['coordinates'] = coords
        # All done
        result = {
            'wkt': wkt.dumps(wkt_obj, decimals=3),
            'repairs': repairs
        }
        return Response(json.dumps(result), 200)
