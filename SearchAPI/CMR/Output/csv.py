import logging
from jinja2 import Environment, PackageLoader

def req_fields_csv():
    fields = [
        'granuleName',
        'platform',
        'sensor',
        'beamMode',
        'configurationName',
        'absoluteOrbit',
        'relativeOrbit',
        'frameNumber',
        'sceneDate',
        'processingDate',
        'processingLevel',
        'startTime',
        'stopTime',
        'centerLat',
        'centerLon',
        'nearStartLat',
        'nearStartLon',
        'farStartLat',
        'farStartLon',
        'nearEndLat',
        'nearEndLon',
        'farEndLat',
        'farEndLon',
        'faradayRotation',
        'flightDirection',
        'downloadUrl',
        'sizeMB',
        'offNadirAngle',
        'insarStackSize',
        'baselinePerp',
        'doppler',
        'groupID',
        'relativeBurstID',
        'absoluteBurstID',
        'fullBurstID',
        'burstIndex',
        'azimuthAnxTime',
        'samplesPerBurst',
        'subswath',
    ]
    return fields

def cmr_to_csv(rgen, includeBaseline=False, addendum=None):
    logging.debug('translating: csv')

    templateEnv = Environment(
        loader=PackageLoader('SearchAPI.CMR', 'templates'),
        autoescape=True
    )

    template = templateEnv.get_template('template.csv')
    for l in template.stream(includeBaseline=includeBaseline, results=rgen()):
        yield l
