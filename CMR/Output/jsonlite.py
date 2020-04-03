import logging
import json
from geomet import wkt

from .json import JSONStreamArray

def cmr_to_jsonlite(rgen, includeBaseline=False, addendum=None):
    logging.debug('translating: jsonlite')

    streamer = JSONLiteStreamArray(rgen, includeBaseline)
    jsondata = {'results': streamer}
    if addendum is not None:
        jsondata.update(addendum)
    
    for p in json.JSONEncoder(indent=2, sort_keys=True).iterencode(jsondata):
        yield p

def unwrap_wkt(wkt_str):
    try:
        wkt_obj = wkt.loads(wkt_str)
        lons = [p[0] for p in wkt_obj['coordinates'][0]]
        if(max(lons) - min(lons) > 180):
            wkt_obj['coordinates'] = [[a if a[0] > 0 else [a[0] + 360, a[1]] for a in wkt_obj['coordinates'][0]]]
        return wkt.dumps(wkt_obj, decimals=6)
    except ValueError as e:
        return wkt_str
    return wkt_str

class JSONLiteStreamArray(JSONStreamArray):
    def getItem(self, p):
        for i in p.keys():
            if p[i] == 'NA' or p[i] == '':
                p[i] = None
        try:
            if float(p['offNadirAngle']) < 0:
                p['offNadirAngle'] = None
        except TypeError:
            pass

        try:
            if float(p['relativeOrbit']) < 0:
                p['relativeOrbit'] = None
        except TypeError:
            pass

        try:
            if p['groupID'] is None:
                p['groupID'] = p['granuleName']
        except TypeError:
            pass

        try:
            p['sizeMB'] = float(p['sizeMB'])
        except TypeError:
            pass

        try:
            p['relativeOrbit'] = int(p['relativeOrbit'])
        except TypeError:
            pass

        try:
            p['frameNumber'] = int(p['frameNumber'])
        except TypeError:
            pass

        try:
            p['absoluteOrbit'] = int(p['absoluteOrbit'])
        except TypeError:
            pass

        result = {
            # Mandatory:
            'dataset': p['platform'],
            'downloadUrl': p['downloadUrl'],
            'fileName': p['fileName'],
            'granuleName': p['granuleName'],
            'groupID': p['groupID'],
            'productID': p['product_file_id'],
            'productType': p['processingLevel'],
            'productTypeDisplay': p['processingTypeDisplay'],
            'startTime': p['startTime'],
            'wkt': p['stringFootprint'],
            'wkt_unwrapped': unwrap_wkt(p['stringFootprint']),
            # Optional:
            'beamMode': p['beamMode'],
            'browse': p['browse'],
            'flightDirection': p['flightDirection'],
            'flightLine': p['flightLine'],
            'frame': p['frameNumber'],
            'missionName': p['missionName'],
            'orbit': p['absoluteOrbit'],
            'path': p['relativeOrbit'],
            'polarization': p['polarization'],
            'sizeMB': p['sizeMB'],
            'stackSize': p['insarStackSize'], # Used for datasets with precalculated stacks
            'thumb': p['thumbnailUrl'],
            # Dataset-specific:
            'faradayRotation': p['faradayRotation'], # ALOS
            'offNadirAngle': p['offNadirAngle'] # ALOS
        }

        if self.includeBaseline:
            result['temporalBaseline'] = p['temporalBaseline']
            result['perpendicularBaseline'] = p['perpendicularBaseline']

        return result
