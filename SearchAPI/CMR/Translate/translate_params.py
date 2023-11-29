import logging
from flask import request
from SearchAPI.CMR.Input import parse_string_list

from SearchAPI.CMR.Translate.datasets import collections_per_platform
from .input_map import input_map

from SearchAPI.CMR.Output import output_translators
import json
import requests
from SearchAPI.asf_env import get_config

def translate_params(p):
    """
    Translate supported params into CMR params
    """

    # pre-search optimization, don't search by platform[] if we can help it
    if (collections := get_platform_collections(p)):
        if p.get('collections') is None:
            p['collections'] = ','.join(collections)
        else:
            p['collections'] += ',' + ','.join(collections)
        
    
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
                raise ValueError(f'Could not repair WKT: {val}')
            val = response['wkt']['wrapped']
        try:
            params[key] = input_map()[key][2](val)
        except ValueError as exc:
            raise ValueError(f'{key}: {exc}') from exc
    
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
                f'Invalid maxResults, must be > 0: {max_results}'
            )
        del params['maxresults']

    return params, output, max_results

def get_platform_collections(params: dict):
    output = []

    if 'platform' in params:
        platforms = parse_string_list(params['platform'])

        # collections limit which collections we search by platform with, 
        # so if there are any we don't have collections for we skip this optimization entirely
        missing = [platform for platform in platforms if collections_per_platform.get(platform.upper()) is None]
        if len(missing) == 0:
            for platform in platforms:
                if (collections := collections_per_platform.get(platform.upper())):
                    output.extend(collections)
            
            return output
        else:
            logging.debug(f"Failed to find concept-ids for platform(s): \"{','.join(missing)}\", defaulting to platform keyword")
