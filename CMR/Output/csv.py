import logging
from jinja2 import Environment, PackageLoader

def cmr_to_csv(rgen, includeBaseline=False):
    logging.debug('translating: csv')

    templateEnv = Environment(
        loader=PackageLoader('CMR', 'templates'),
        autoescape=True
    )

    template = templateEnv.get_template('template.csv')
    for l in template.stream(includeBaseline=includeBaseline, results=rgen()):
        yield l
