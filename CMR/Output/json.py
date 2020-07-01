import logging
import json

def req_fields_json():
    fields = [
        'absoluteOrbit',
        'beamMode',
        'beamModeType',
        'beamSwath',
        'browse',
        'catSceneId',
        'centerLat',
        'centerLon',
        'collectionName',
        'configurationName',
        'doppler',
        'downloadUrl',
        'farEndLat',
        'farEndLon',
        'farStartLat',
        'farStartLon',
        'faradayRotation',
        'fileName',
        'finalFrame',
        'firstFrame',
        'flightDirection',
        'flightLine',
        'formatName',
        'frameNumber',
        'frequency',
        'granuleName',
        'granuleType',
        'groupID',
        'incidenceAngle',
        'insarGrouping',
        'insarStackSize',
        'lookDirection',
        'masterGranule',
        'md5sum',
        'missionName',
        'nearEndLat',
        'nearEndLon',
        'nearStartLat',
        'nearStartLon',
        'offNadirAngle',
        'percentCoherence',
        'percentTroposphere',
        'percentUnwrapped',
        'platform',
        'pointingAngle',
        'polarization',
        'processingDate',
        'processingDescription',
        'processingLevel',
        'processingType',
        'processingTypeDisplay',
        'productName',
        'product_file_id',
        'relativeOrbit',
        'sarSceneId',
        'sceneDate',
        'sceneDateString',
        'sceneId',
        'sensor',
        'sizeMB',
        'slaveGranule',
        'startTime',
        'status',
        'stopTime',
        'stringFootprint',
        'thumbnailUrl',
        'track',
        'varianceTroposphere'
    ]
    return fields

def cmr_to_json(rgen, includeBaseline=False, addendum=None):
    logging.debug('translating: json')

    streamer = JSONStreamArray(rgen, includeBaseline)

    for p in json.JSONEncoder(indent=2, sort_keys=True).iterencode([streamer]):
        yield p

# Some trickery is required to make JSONEncoder().iterencode take any ol' generator,
# this approach works without slurping the list into memory
class JSONStreamArray(list):
    def __init__(self, gen, includeBaseline):
        self.gen = gen
        self.includeBaseline = includeBaseline

        # need to make sure we actually have results so we can intelligently set __len__, otherwise
        # iterencode behaves strangely and will output invalid json
        self.first_result = None
        self.len = 0
        for p in self.gen():
            if p is not None:
                self.first_result = p
                self.len = 1
                break

    def __iter__(self):
        return self.streamDicts()

    def __len__(self):
        return self.len

    def streamDicts(self):
        for p in self.gen():
            if p is not None:
                yield self.getItem(p)

    # Override this method for other json-based output formats (i.e. geojson)
    def getItem(self, p):
        legacy_json_keys = req_fields_json()
        if self.includeBaseline:
            legacy_json_keys.extend(['temporalBaseline', 'perpendicularBaseline'])

        p['browse'] = p['browse'][0] if len(p['browse']) > 0 else None

        return dict((k, p[k]) for k in legacy_json_keys if k in p)
