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

def canInsar(p):
    if p['platform'] in ['ALOS', 'RADARSAT-1', 'JERS-1', 'ERS-1', 'ERS-2'] and \
        p.get('insarGrouping') not in [None, 0, '0', 'NA']:
        return True
    elif None not in [
        p['sv_pos_pre'], p['sv_pos_post'],
        p['sv_vel_pre'], p['sv_vel_post'],
        p['sv_t_pos_pre'], p['sv_t_pos_post'],
        p['sv_t_vel_pre'], p['sv_t_vel_post']]:
        return True
    else:
        return False

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

        result = {            'beamMode': p['beamMode'],
            'browse': p['browse'],
            'canInSAR': canInsar(p),
            'dataset': p['platform'],
            'downloadUrl': p['downloadUrl'],
            'faradayRotation': p['faradayRotation'], # ALOS
            'fileName': p['fileName'],
            'flightDirection': p['flightDirection'],
            'flightLine': p['flightLine'],
            'frame': p['frameNumber'],
            'granuleName': p['granuleName'],
            'groupID': p['groupID'],
            'instrument': p['sensor'],
            'missionName': p['missionName'],
            'offNadirAngle': p['offNadirAngle'], # ALOS
            'orbit': p['absoluteOrbit'],
            'path': p['relativeOrbit'],
            'polarization': p['polarization'],
            'pointingAngle': p['pointingAngle'],
            'productID': p['product_file_id'],
            'productType': p['processingLevel'],
            'productTypeDisplay': p['processingTypeDisplay'],
            'sizeMB': p['sizeMB'],
            'stackSize': p['insarStackSize'], # Used for datasets with precalculated stacks
            'startTime': p['startTime'],
            'thumb': p['thumbnailUrl'],
            'wkt': p['stringFootprint'],
            'wkt_unwrapped': unwrap_wkt(p['stringFootprint'])
        }

        if self.includeBaseline:
            result['temporalBaseline'] = p['temporalBaseline']
            result['perpendicularBaseline'] = p['perpendicularBaseline']

        return result
