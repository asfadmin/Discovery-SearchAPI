import logging
from jinja2 import Environment, PackageLoader

def cmr_to_csv(rgen):
    logging.debug('translating: csv')

    templateEnv = Environment(
        loader=PackageLoader('CMR', 'templates'),
        autoescape=True
    )

    template = templateEnv.get_template('template.csv')
    for l in template.stream(results=rgen()):
        yield l
