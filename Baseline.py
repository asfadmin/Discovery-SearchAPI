import logging
import requests
import json
import dateparser
from flask import request
import random

from asf_env import get_config

def get_stack(master):
    try:
        stack_params = get_stack_params(master)
    except ValueError as e:
        raise e

    stack_params['output'] = 'jsonlite2'
    if hasattr(request, 'temp_maturity'):
        stack_params['maturity'] = request.temp_maturity
    s = requests.Session()
    url = request.url_root + 'services/load/param'
    stack = json.loads(s.post(url, data=stack_params).text)
    stack['warnings'] = []

    master, stack = check_master(master, stack)

    stack['results'] = calculate_temporal_baselines(master, stack['results'])

    # totally faking perpendicular baseline data for the moment, come at me bro
    for product in stack['results']:
        random.seed(product['gn']) # lol
        product['pb'] = 0 if product['gn'] == master else random.randrange(-500, 500)

    if len(stack['warnings']) <= 0:
        del stack['warnings']
    return stack

def get_stack_params(master):
    url = request.url_root + 'services/load/param'
    s = requests.Session()
    p = {'granule_list': master, 'output': 'jsonlite'}
    if hasattr(request, 'temp_maturity'):
        p['maturity'] = request.temp_maturity
    results = json.loads(s.post(url, data=p).text)['results']
    if len(results) <= 0:
        raise ValueError(f'Requested master not found: {master}')

    stack_params = {
        'beamMode': None,
        'dataset': None,
        'flightDirection': None,
        'frame': None,
        'lookDirection': None,
        'offNadirAngle': None,
        'path': None,
        'polarization': None
    }

    for product in results:
        for key in stack_params.keys():
            if stack_params[key] is None and key in product and product[key] is not None:
                stack_params[key] = product[key]

    stack_params = tweak_stack_params(stack_params)
    stack_params = rename_stack_params(stack_params)

    return stack_params

# Make dataset-specific adjustments to stack constraints
def tweak_stack_params(params):
    def tweak_alos(params):
        return params

    def tweak_ers(params):
        del params['lookDirection']
        del params['offNadirAngle']

        params['dataset'] = 'ERS' # Use the API's multi-dataset alias for E1/E2 tandem stacks

        return params

    def tweak_jers(params):
        del params['lookDirection']
        del params['offNadirAngle']

        return params

    def tweak_rsat(params):
        del params['offNadirAngle']

        return params

    def tweak_sentinel(params):
        #del params['frame'] # questionable; proof of concept used spatial AoI matching
        del params['offNadirAngle']

        if params['polarization'] in ['HH', 'HH+HV']:
            params['polarization'] = 'HH,HH+HV'
        elif params['polarization'] in ['VV', 'VV+VH']:
            params['polarization'] = 'VV,VV+VH'
        f = params['frame']
        params['frame'] = f'{f-2}-{f+2}' # FIXME: OG proof of concept used masster as AoI, look into that
        params['dataset'] = 'S1' # Use the API's multi-dataset alias for S1/S2 tandem stacks

        return params

    tweak_map = {
        'ALOS':        tweak_alos,
        'ERS-1':       tweak_ers,
        'ERS-2':       tweak_ers,
        'JERS-1':      tweak_jers,
        'RADARSAT-1':  tweak_rsat,
        'Sentinel-1A': tweak_sentinel,
        'Sentinel-1B': tweak_sentinel,
    }
    return tweak_map[params['dataset']](params)

# Convenience method to convert jsonlite names to SearchAPI names
def rename_stack_params(params):
    rename_map = {
        'beamMode':         'beammode',
        'dataset':          'platform',
        'flightDirection':  'flightdirection',
        'frame':            'frame', # asfframe?
        'lookDirection':    'lookdirection',
        'offNadirAngle':    'offnadirangle',
        'path':             'relativeorbit',
        'polarization':     'polarization'
    }
    renamed_params = {}
    for p in params.keys():
        renamed_params[rename_map[p]] = params[p]
    return renamed_params

def check_master(master, stack):
    if master not in [product['gn'] for product in stack['results']]:
        master = stack[0]['gn']
        stack['warnings'].append({'NEW_MASTER': f'A new master had to be selected in order to calculate baseline values: {master}'})
    return master, stack

def calculate_temporal_baselines(master, stack):
    for product in stack:
        if product['gn'] == master:
            master_start = dateparser.parse(product['st'])
            break
    for product in stack:
        if product['gn'] == master:
            product['tb'] = 0
        else:
            start = dateparser.parse(product['st'])
            product['tb'] = (start - master_start).days
    return stack
