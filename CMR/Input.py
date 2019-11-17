import dateparser
import re
from geomet import wkt, InvalidGeoJSONException

# Parse and validate a string: "abc"
def parse_string(v):
    if not len(v) > 0:
        raise ValueError('Invalid string: Empty string: {0}'.format(v))
    try:
        return '{0}'.format(v)
    except ValueError: # If this happens, the following line would fail as well...
        raise ValueError('Invalid string: {0}'.format(v))

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

# Parse and validate a date: "1991-10-01T00:00:00Z"
def parse_date(v):
    d = dateparser.parse(v)
    if d is None:
        raise ValueError('Invalid date: {0}'.format(v))
    return dateparser.parse(v).strftime('%Y-%m-%dT%H:%M:%SZ')

# Parse and validate a date range: "1991-10-01T00:00:00Z,1991-10-02T00:00:00Z"
def parse_date_range(v):
    dates = v.split(',')
    if len(dates) != 2:
        raise ValueError('Invalid date range: must be two comma-separated dates')
    return '{0},{1}'.format(parse_date(dates[0]), parse_date(dates[1]))

# Parse and validate a numeric value range, using h() to validate each value: "3-5", "1.1-12.3"
def parse_range(v, h):
    try:
        v = v.replace(' ', '')
        m = re.search(r'^(-?\d+(\.\d*)?)-(-?\d+(\.\d*)?)$', v)
        if m is None:
            raise ValueError('Invalid range: {0}'.format(v))
        a = [h(m.group(1)), h(m.group(3))]
        if a[0] > a[1]:
            raise ValueError()
        if a[0] == a[1]:
            a = a[0]
    except ValueError as e:
        raise ValueError('Invalid range: {0}'.format(e))
    return a

# Parse and validate an integer range: "3-5"
def parse_int_range(v):
    try:
        return parse_range(v, parse_int)
    except ValueError as e:
        raise ValueError('Invalid int range: {0}'.format(e))

# Parse and validate a float range: "1.1-12.3"
def parse_float_range(v):
    try:
        return parse_range(v, parse_float)
    except ValueError as e:
        raise ValueError('Invalid float range: {0}'.format(e))

# Parse and validate a list of values, using h() to validate each value: "a,b,c", "1,2,3", "1.1,2.3"
def parse_list(v, h):
    try:
        return [h(a) for a in v.split(',')]
    except ValueError as e:
        raise ValueError('Invalid list: {0}'.format(e))

# Parse and validate a list of strings: "foo,bar,baz"
def parse_string_list(v):
    try:
        return parse_list(v, parse_string)
    except ValueError as e:
        raise ValueError('Invalid string list: {0}'.format(e))

# Parse and validate a list of integers: "1,2,3"
def parse_int_list(v):
    try:
        return parse_list(v, parse_int)
    except ValueError as e:
        raise ValueError('Invalid int list: {0}'.format(e))

# Parse and validate a list of floats: "1.1,2.3,4.5"
def parse_float_list(v):
    try:
        return parse_list(v, parse_float)
    except ValueError as e:
        raise ValueError('Invalid float list: {0}'.format(e))

# Parse and validate a number or a range, using h() to validate each value: "1", "4.5", "3-5", "10.1-13.4"
def parse_number_or_range(v, h):
    try:
        m = re.search(r'^(-?\d+(\.\d*)?)$', v)
        if m is not None:
            return h(v)
        return parse_range(v, h)
    except ValueError as e:
        raise ValueError('Invalid number or range: {0}'.format(e))

# Parse and validate a list of numbers or number ranges, using h() to validate each value: "1,2,3-5", "1.1,1.4,5.1-6.7"
def parse_number_or_range_list(v, h):
    try:
        v = v.replace(' ', '')
        return [parse_number_or_range(x, h) for x in v.split(',')]
    except ValueError as e:
        raise ValueError('Invalid number or range list: {0}'.format(e))

# Parse and validate a list of integers or integer ranges: "1,2,3-5"
def parse_int_or_range_list(v):
    try:
        return parse_number_or_range_list(v, parse_int)
    except ValueError as e:
        raise ValueError('Invalid int or range list: {0}'.format(e))

# Parse and validate a list of float or float ranges: "1.0,2.0,3.0-5.0"
def parse_float_or_range_list(v):
    try:
        return parse_number_or_range_list(v, parse_float)
    except ValueError as e:
        raise ValueError('Invalid float or range list: {0}'.format(e))

# Parse and validate a coordinate string
def parse_coord_string(v):
    v = v.split(',')
    for c in v:
        try:
            float(c)
        except ValueError:
            raise ValueError('Invalid coordinate: {0}'.format(c))
    if len(v) % 2 != 0:
        raise ValueError('Invalid coordinate list, odd number of values provided: {0}'.format(v))
    return ','.join(v)

# Parse and validate a bbox coordinate string
def parse_bbox_string(v):
    try:
        v = parse_coord_string(v)
    except ValueError as e:
        raise ValueError('Invalid bbox: {0}'.format(e))
    if len(v.split(',')) != 4:
        raise ValueError('Invalid bbox, must be 4 values: {0}'.format(v))
    return v

# Parse and validate a point coordinate string
def parse_point_string(v):
    try:
        v = parse_coord_string(v)
    except ValueError as e:
        raise ValueError('Invalid point: {0}'.format(e))
    if len(v.split(',')) != 2:
        raise ValueError('Invalid point, must be 2 values: {0}'.format(v))
    return v

# Parse a WKT and convert it to a coordinate string
# NOTE: If given an empty ("POINT EMPTY") shape, will return "point:". Should it throw instead?
def parse_wkt(v):
    try:
        wkt_json = wkt.loads(str(v).upper())
    except (ValueError, AttributeError, InvalidGeoJSONException) as e:
        raise ValueError('Cannot load WKT: {0}. Error: {1}'.format(v, str(e)))
    # take note of the WKT type
    if wkt_json['type'].upper() not in ["POINT","LINESTRING", "POLYGON"]:
        raise ValueError('Unsupported WKT: {0}.'.format(v))
    
    if wkt_json['type'].upper() == "POLYGON":
        coords = wkt_json['coordinates']
        # If not an empty poly, take out the hole:
        # (Also de-nest it in the process)
        if len(wkt_json['coordinates']) != 0:
            coords = coords[0]
    elif wkt_json['type'].upper() == "LINESTRING":
        coords = wkt_json['coordinates']
    else: # type == POINT
        coords = [wkt_json['coordinates']]
    # Turn [[x,y],[x,y]] to [x,y,x,y]:
    coords = [x for x in sum(coords, [])]
    # Turn any "6e8" to a literal number. (As a sting):
    coords = ['{:.16f}'.format(float(cord)) for cord in coords]
    return '{0}:{1}'.format(wkt_json['type'].lower(), ','.join(coords))
