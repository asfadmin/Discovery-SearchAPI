from flask import request
from .input_map import input_map

from CMR.Output import output_translators
import json
import requests
from asf_env import get_config

def translate_params(p):
    """
    Translate supported params into CMR params
    """
    params = {}

    for key in p:
        val = p[key]
        key = key.lower()
        if key not in input_map():
            raise ValueError(f'Unsupported parameter: {key}')
        if key == 'intersectswith': # Gotta catch this suuuuper early
            s = requests.Session()
            repair_params = dict({'wkt': val})
            try:
                repair_params['maturity'] = request.temp_maturity
            except AttributeError:
                pass
            response = json.loads(s.post(get_config()['this_api'] + '/services/utils/wkt', data=repair_params).text)
            if 'errors' in response:
                raise ValueError('Could not repair WKT: {0}'.format(val))
            val = response['wkt']['wrapped']
        try:
            params[key] = input_map()[key][2](val)
        except ValueError as exc:
            raise ValueError(f'{key}: {exc}')

    # be nice to make this not a special case
    output = 'metalink'

    if 'output' in params and params['output'].lower() in output_translators():
        output = params['output'].lower()

    if 'output' in params:
        del params['output']
    max_results = None

    if 'maxresults' in params:
        max_results = params['maxresults']
        if max_results < 1:
            raise ValueError(
                'Invalid maxResults, must be > 0: {0}'.format(max_results)
            )
        del params['maxresults']

    return params, output, max_results
