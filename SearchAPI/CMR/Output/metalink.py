import logging
from jinja2 import Environment, PackageLoader

def req_fields_metalink():
    fields = [
        'fileName',
        'downloadUrl',
        'md5sum',
        'bytes',
    ]
    return fields

def cmr_to_metalink(rgen, includeBaseline=False, addendum=None):
    logging.debug('translating: metalink')

    templateEnv = Environment(
        loader=PackageLoader('SearchAPI.CMR', 'templates'),
        autoescape=True
    )

    template = templateEnv.get_template('template.metalink')
    for l in template.stream(results=rgen()):
        yield l
