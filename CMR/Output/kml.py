import logging
from jinja2 import Environment, PackageLoader

def cmr_to_kml(rgen):
    logging.debug('translating: kml')

    templateEnv = Environment(
        loader=PackageLoader('CMR', 'templates'),
        autoescape=True
    )
    
    template = templateEnv.get_template('template.kml')
    for l in template.stream(results=rgen()):
        yield l
