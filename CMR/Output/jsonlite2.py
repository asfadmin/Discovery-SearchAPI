import logging
import json
from .jsonlite import JSONLiteStreamArray

def cmr_to_jsonlite2(rgen):
    logging.debug('translating: jsonlite')

    streamer = JSONLite2StreamArray(rgen)

    for p in json.JSONEncoder(sort_keys=True, separators=(',', ':')).iterencode({'results': streamer}):
        yield p

class JSONLite2StreamArray(JSONLiteStreamArray):
    @staticmethod
    def getItem(p):
         # pre-processing of the result is the same as in the base jsonlite streamer,
         # so use that and then rename/substitute fields
        p = JSONLiteStreamArray.getItem(p)
        return {
            # Mandatory:
            'd': p['dataset'],
            'du': p['downloadUrl'].replace(p['granuleName'], '{gn}'),
            'fn': p['fileName'].replace(p['granuleName'], '{gn}'),
            'gn': p['granuleName'],
            'gid': p['groupID'].replace(p['granuleName'], '{gn}'),
            'pid': p['productID'].replace(p['granuleName'], '{gn}'),
            'pt': p['productType'],
            'ptd': p['productTypeDisplay'],
            'st': p['startTime'],
            'w': p['wkt'],
            'wu': p['wkt_unwrapped'],
            # Optional:
            'bm': p['beamMode'],
            'b': [a.replace(p['granuleName'], '{gn}') for a in p['browse']] if p['browse'] is not None else p['browse'],
            'fd': p['flightDirection'],
            'fl': p['flightLine'],
            'f': p['frame'],
            'mn': p['missionName'],
            'o': p['orbit'],
            'p': p['path'],
            'po': p['polarization'],
            's': p['sizeMB'],
            'ss': p['stackSize'], # Used for datasets with precalculated stacks
            't': p['thumb'].replace(p['granuleName'], '{gn}') if p['thumb'] is not None else p['thumb'],
            # Dataset-specific:
            'fr': p['faradayRotation'], # ALOS
            'on': p['offNadirAngle'] # ALOS
        }
