from SearchAPI.CMR.Input import (
    parse_int, parse_float, parse_string, parse_wkt, parse_date,
    parse_string_list, parse_int_list, parse_int_or_range_list,
    parse_float_or_range_list,
    parse_coord_string, parse_bbox_string, parse_point_string
)

def input_map():
    """
    Supported input parameters and their associated CMR parameters
    """
    parameter_map = {
#       API parameter           CMR parameter               CMR format strings                  Parser
        'output':               [None,                      '{0}',                              parse_string],
        'maxresults':           [None,                      '{0}',                              parse_int],
        'absoluteorbit':        ['orbit_number',            '{0}',                              parse_int_or_range_list],
        'asfframe':             ['attribute[]',             'int,FRAME_NUMBER,{0}',             parse_int_or_range_list],
        'maxbaselineperp':      ['attribute[]',             'float,INSAR_BASELINE,,{0}',        parse_float],
        'minbaselineperp':      ['attribute[]',             'float,INSAR_BASELINE,{0},',        parse_float],
        'beammode':             ['attribute[]',             'string,BEAM_MODE,{0}',             parse_string_list],
        'beamswath':            ['attribute[]',             'string,BEAM_MODE_TYPE,{0}',        parse_string_list],
        'collectionname':       ['attribute[]',             'string,MISSION_NAME,{0}',          parse_string],
        'maxdoppler':           ['attribute[]',             'float,DOPPLER,,{0}',               parse_float],
        'mindoppler':           ['attribute[]',             'float,DOPPLER,{0},',               parse_float],
        'maxfaradayrotation':   ['attribute[]',             'float,FARADAY_ROTATION,,{0}',      parse_float],
        'minfaradayrotation':   ['attribute[]',             'float,FARADAY_ROTATION,{0},',      parse_float],
        'flightdirection':      ['attribute[]',             'string,ASCENDING_DESCENDING,{0}',  parse_string],
        'flightline':           ['attribute[]',             'string,FLIGHT_LINE,{0}',           parse_string],
        'frame':                ['attribute[]',             'int,CENTER_ESA_FRAME,{0}',         parse_int_or_range_list],
        'granule_list':         ['readable_granule_name[]', '{0}',                              parse_string_list],
        'product_list':         ['granule_ur[]',            '{0}',                              parse_string_list],
        'maxinsarstacksize':    ['attribute[]',             'int,INSAR_STACK_SIZE,,{0}',        parse_int],
        'mininsarstacksize':    ['attribute[]',             'int,INSAR_STACK_SIZE,{0},',        parse_int],
        'intersectswith':       [None,                      '{0}',                              parse_wkt],
        'lookdirection':        ['attribute[]',             'string,LOOK_DIRECTION,{0}',        parse_string],
        'offnadirangle':        ['attribute[]',             'float,OFF_NADIR_ANGLE,{0}',        parse_float_or_range_list],
        'platform':             ['platform[]',              '{0}',                              parse_string_list],
        'asfplatform':          ['attribute[]',             'string,ASF_PLATFORM,{0}',          parse_string_list],
        'polarization':         ['attribute[]',             'string,POLARIZATION,{0}',          parse_string_list],
        'polygon':              ['polygon',                 '{0}',                              parse_coord_string], # intersectsWith ends up here
        'linestring':           ['line',                    '{0}',                              parse_coord_string], # or here
        'point':                ['point',                   '{0}',                              parse_point_string], # or here
        'bbox':                 ['bounding_box',            '{0}',                              parse_bbox_string],
        'processinglevel':      ['attribute[]',             'string,PROCESSING_TYPE,{0}',       parse_string_list],
        'relativeorbit':        ['attribute[]',             'int,PATH_NUMBER,{0}',              parse_int_or_range_list],
        'processingdate':       ['updated_since',           '{0}',                              parse_date],
        'start':                [None,                      '{0}',                              parse_date],
        'end':                  [None,                      '{0}',                              parse_date],
        'season':               [None,                      '{0}',                              parse_int_list],
        'temporal':             ['temporal',                '{0}',                              None], # start/end end up here
        'groupid':              ['attribute[]',             'string,GROUP_ID,{0}',              parse_string_list],
        'insarstackid':         ['attribute[]',             'int,INSAR_STACK_ID,{0}',           parse_string],
        'instrument':           ['instrument[]',            '{0}',                              parse_string],
        'relativeburstid':      ['attribute[]',             'int,RELATIVE_BURST_ID,{0}',        parse_int_list],
    }

    return parameter_map
