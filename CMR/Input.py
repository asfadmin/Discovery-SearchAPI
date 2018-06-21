import dateparser
import re
from geomet import wkt

# Parse and validate a string: "abc"
def parse_string(v):
    return '{0}'.format(v)

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
    return dateparser.parse(v).strftime('%Y-%m-%dT%H:%M:%SZ')

# Parse and validate a date range: "1991-10-01T00:00:00Z,1991-10-02T00:00:00Z"
def parse_date_range(v):
    dates = v.split(',')
    if len(dates) != 2:
        raise ValueError('Invalid date range: must be two comma-separated dates')
    return '{0},{1}'.format(parse_date(dates[0]), parse_date(dates[1]))

# Parse and validate a numeric value range, using h() to validate each value: "3-5", "1.1-12.3"
def parse_range(v, h):
    v = v.replace(' ', '')
    m = re.search(r'^(-?\d+(\.\d*)?)-(-?\d+(\.\d*)?)$', v)
    try:
        a = [h(m.group(1)), h(m.group(3))]
        if a[0] > a[1]:
            raise ValueError()
    except ValueError:
        raise ValueError('Invalid range: {0}'.format(v))
    return a

# Parse and validate an integer range: "3-5"
def parse_int_range(v):
    return parse_range(v, parse_int)

# Parse and validate a float range: "1.1-12.3"
def parse_float_range(v):
    return parse_range(v, parse_float)

# Parse and validate a list of values, using h() to validate each value: "a,b,c", "1,2,3", "1.1,2.3"
def parse_list(v, h):
    return [h(a) for a in v.split(',')]

# Parse and validate a list of strings: "foo,bar,baz"
def parse_string_list(v):
    return parse_list(v, '{0}'.format)

# Parse and validate a list of integers: "1,2,3"
def parse_int_list(v):
    return parse_list(v, parse_int)

# Parse and validate a list of floats: "1.1,2.3,4.5"
def parse_float_list(v):
    return parse_list(v, parse_float)

# Parse and validate a number or a range, using h() to validate each value: "1", "4.5", "3-5", "10.1-13.4"
def parse_number_or_range(v, h):
    m = re.search(r'^(-?\d+(\.\d*)?)$', v)
    if m is not None:
        return h(v)
    return parse_range(v, h)
    
# Parse and validate a list of numbers or number ranges, using h() to validate each value: "1,2,3-5", "1.1,1.4,5.1-6.7"
def parse_number_or_range_list(v, h):
    v = v.replace(' ', '')
    return [parse_number_or_range(x, h) for x in v.split(',')]

# Parse and validate a list of integers or integer ranges: "1,2,3-5"
def parse_int_or_range_list(v):
    return parse_number_or_range_list(v, parse_int)

# Parse and validate a list of integers or integer ranges: "1,2,3-5"
def parse_float_or_range_list(v):
    return parse_number_or_range_list(v, parse_float)

# Parse and validate a coordinate string
def parse_coord_string(v):
    v = v.split(',')
    for c in v:
        try:
            float(c)
        except ValueError:
            raise ValueError('Invalid polygon: {0}'.format(v))
    return ','.join(v)

# Parse a WKT and convert it to a coordinate string
def parse_wkt(v):
    # take note of the WKT type
    t = re.match(r'linestring|point|polygon', v.lower())
    if t is None:
        raise ValueError('Unsupported WKT: {0}'.format(v))
    t = t.group(0)
    p = wkt.loads(v.upper())['coordinates']
    if t in ['polygon']:
        p = p[0] # ignore any subsequent parts like holes, they aren't supported by CMR
    if t in ['polygon', 'linestring']: # de-nest the coord list if needed
        p = [x for x in sum(p, [])]
    p = [str(x) for x in p]
    return '{0}:{1}'.format(t, ','.join(p))
