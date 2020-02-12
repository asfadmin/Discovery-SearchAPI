import logging
import json

def cmr_to_json(rgen):
    logging.debug('translating: json')

    streamer = JSONStreamArray(rgen)

    for p in json.JSONEncoder(indent=2, sort_keys=True).iterencode([streamer]):
        yield p

# Some trickery is required to make JSONEncoder().iterencode take any ol' generator,
# this approach works without slurping the list into memory
class JSONStreamArray(list):
    def __init__(self, gen):
        self.gen = gen

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
        p['browse'] = p['browse'][0] if len(p['browse']) > 0 else None
        legacy_json_keys = [
            'sceneSize',
            'absoluteOrbit',
            'farEndLat',
            'sensor',
            'farStartLat',
            'processingTypeName',
            'finalFrame',
            'lookAngle',
            'processingType',
            'startTime',
            'stringFootprint',
            'doppler',
            'baselinePerp',
            'sarSceneId',
            'insarStackSize',
            'centerLat',
            'processingDescription',
            'product_file_id',
            'nearEndLon',
            'farEndLon',
            'percentTroposphere',
            'frameNumber',
            'percentCoherence',
            'nearStartLon',
            'sceneDate',
            'sceneId',
            'productName',
            'platform',
            'masterGranule',
            'thumbnailUrl',
            'percentUnwrapped',
            'beamSwath',
            'firstFrame',
            'insarGrouping',
            'centerLon',
            'faradayRotation',
            'fileName',
            'offNadirAngle',
            'granuleName',
            'frequency',
            'catSceneId',
            'farStartLon',
            'processingDate',
            'missionName',
            'relativeOrbit',
            'flightDirection',
            'granuleType',
            'configurationName',
            'polarization',
            'stopTime',
            'browse',
            'nearStartLat',
            'flightLine',
            'status',
            'formatName',
            'nearEndLat',
            'downloadUrl',
            'incidenceAngle',
            'processingTypeDisplay',
            'thumbnail',
            'track',
            'collectionName',
            'sceneDateString',
            'beamMode',
            'beamModeType',
            'processingLevel',
            'lookDirection',
            'varianceTroposphere',
            'slaveGranule',
            'sizeMB',
            'groupID',
            'md5sum'
        ]

        return dict((k, p[k]) for k in legacy_json_keys if k in p)
