import logging
from jinja2 import Environment, PackageLoader

def req_fields_kml():
    fields = [
        'absoluteOrbit',
        'browse',
        'configurationName',
        'downloadUrl',
        'faradayRotation',
        'flightDirection',
        'frameNumber',
        'granuleName',
        'offNadirAngle',
        'platform',
        'pointingAngle',
        'processingTypeDisplay',
        'relativeOrbit',
        'sceneDate',
        'shape',
        'startTime',
        'stopTime',
        'thumbnailUrl'
    ]
    return fields

def cmr_to_kml(rgen, includeBaseline=False, addendum=None):
    logging.debug('translating: kml')

    templateEnv = Environment(
        loader=PackageLoader('SearchAPI.CMR', 'templates'),
        autoescape=True
    )

    template = templateEnv.get_template('template.kml')
    for l in template.stream(includeBaseline=includeBaseline, results=rgen()):
        yield l
