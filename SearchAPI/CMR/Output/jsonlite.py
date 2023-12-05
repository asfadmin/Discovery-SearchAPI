import logging
import json
from geomet import wkt

def req_fields_jsonlite():
    fields = [
        'absoluteOrbit',
        'beamMode',
        'browse',
        'canInsar',
        'downloadUrl',
        'faradayRotation',
        'fileName',
        'flightDirection',
        'flightLine',
        'frameNumber',
        'granuleName',
        'groupID',
        'insarStackSize',
        'missionName',
        'offNadirAngle',
        'platform',
        'pointingAngle',
        'polarization',
        'processingLevel',
        'processingTypeDisplay',
        'product_file_id',
        'relativeOrbit',
        'sensor',
        'sizeMB',
        'startTime',
        'stopTime',
        'stringFootprint',
        'thumbnailUrl',
        'absoluteBurstID',
        'relativeBurstID',
        'fullBurstID',
        'burstIndex',
        'azimuthTime',
        'azimuthAnxTime',
        'samplesPerBurst',
        'subswath',
        'pgeVersion',
        'operaBurstID',
        'additionalUrls'
    ]
    return fields


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
    except ValueError:
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
            if p['downloadUrl'] is None:
                p['downloadUrl'] = ''
        except TypeError:
            pass

        try:
            if p['granuleName'] is None:
                p['granuleName'] = p['product_file_id']
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
            'beamMode': p['beamMode'],
            'browse': p['browse'],
            'canInSAR': p['canInsar'],
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
            'stopTime': p['stopTime'],
            'thumb': p['thumbnailUrl'],
            'wkt': p['stringFootprint'],
            'wkt_unwrapped': unwrap_wkt(p['stringFootprint']),
            'pgeVersion': p['pgeVersion']
        }

        if self.includeBaseline:
            result['temporalBaseline'] = p['temporalBaseline']
            result['perpendicularBaseline'] = p['perpendicularBaseline']
        
        if p.get('processingLevel') == 'BURST': # is a burst product
            burst = {}
            burst['relativeBurstID'] = int(p['relativeBurstID'])
            burst['absoluteBurstID'] = int(p['absoluteBurstID'])
            burst['fullBurstID'] = p['fullBurstID']
            burst['burstIndex'] = int(p['burstIndex'])
            burst['azimuthTime']  = p['azimuthTime']
            burst['azimuthAnxTime'] = float(p['azimuthAnxTime'])
            burst['samplesPerBurst'] = int(p['samplesPerBurst'])
            burst['subswath'] = p['subswath']

            result['burst'] = burst

        if p.get('operaBurstID') is not None or result['productID'].startswith('OPERA'):
            result['opera'] = {
                'operaBurstID': p.get('operaBurstID'),
                'additionalUrls': p.get('additionalUrls'),
            }
            if p.get('validityStartDate'):
                result['opera']['validityStartDate'] = p.get('validityStartDate')

        return result
