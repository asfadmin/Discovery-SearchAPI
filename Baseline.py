import logging
import dateparser
from CMR.Translate import translate_params
from CMR.Query import CMRQuery

import random

precalc_datasets = ['AL', 'R1', 'E1', 'E2', 'J1']

def get_stack(master, product_type=None, is_count=False):
    warnings = None

    try:
        stack_params = get_stack_params(master, product_type)
    except ValueError as e:
        if is_count:
            return 0, None
        else:
            raise e

    logging.debug(stack_params)
    if is_count:
        return 1, None

    stack = query_stack(stack_params)

    if len(stack) <= 0:
        raise ValueError(f'No products found matching stack parameters')

    master, stack, warnings = check_master(master, stack)

    stack = calculate_temporal_baselines(master, stack)

    if get_platform(master) in precalc_datasets:
        stack = offset_perpendicular_baselines(master, stack)
    else:
        stack = calculate_perpendicular_baselines(master, stack)


    return stack, warnings

def get_stack_params(master, product_type):
    params = {'granule_list': master}
    if product_type is not None:
        params['processingLevel'] = product_type
    params, output, max_results = translate_params(params)
    query = CMRQuery(
        params=dict(params)
    )
    master_results = [product for product in query.get_results()]
    if len(master_results) <= 0:
        raise ValueError(f'Requested master not found: {master}')

    stack_params = {}
    if product_type is not None:
        stack_params['processingLevel'] = product_type

    stack_params['platform'] = master_results[0]['platform']

    #shortcut the stacking for legacy datasets with precalculated stacks and baselines
    if get_platform(master) in precalc_datasets:
        if master_results[0]['insarGrouping'] is not None and master_results[0]['insarGrouping'] not in ['NA']:
            stack_params['insarstackid'] = master_results[0]['insarGrouping']
            return stack_params
        else:
            # if it's a precalc stack with no stack ID, we gotta bail because we don't have state vectors to fall back on
            raise ValueError(f'Requested master did not have required baseline stack ID: {master}')

    # build a stack from scratch if it's a non-precalc dataset with state vectors
    if get_platform(master) in ['S1']:
        stack_params['beamMode'] = master_results[0]['beamMode']
        stack_params['flightDirection'] = master_results[0]['flightDirection']
        stack_params['lookDirection'] = master_results[0]['lookDirection']
        stack_params['relativeorbit'] = master_results[0]['relativeOrbit'] # path
        stack_params['polarization'] = master_results[0]['polarization']
        if params['polarization'] in ['HH', 'HH+HV']:
            params['polarization'] = 'HH,HH+HV'
        elif params['polarization'] in ['VV', 'VV+VH']:
            params['polarization'] = 'VV,VV+VH'
        stack_params['intersectsWith'] = f"POINT({master_results[0]['centerLon']} {master_results[0]['centerLat']})" # flexible alternative to frame

    return stack_params

def query_stack(params):
    params, output, max_results = translate_params(params)
    query = CMRQuery(
        params=dict(params)
    )
    return [product for product in query.get_results()]

def check_master(master, stack):
    warnings = None
    if master not in [product['granuleName'] for product in stack]:
        master = stack[0]['granuleName']
        warnings = [{'NEW_MASTER': f'A new master had to be selected in order to calculate baseline values.'}]
    return master, stack, warnings

def get_platform(master):
    return master[0:2].upper()

def get_default_product_type(master):
    if get_platform(master) in ['AL']:
        return 'L1.1'
    if get_platform(master) in ['R1', 'E1', 'E2', 'J1']:
        return 'L0'
    if get_platform(master) in ['S1']:
        return 'SLC'
    return None

def calculate_temporal_baselines(master, stack):
    for product in stack:
        if product['granuleName'] == master:
            master_start = dateparser.parse(product['startTime'])
            break
    for product in stack:
        if product['granuleName'] == master:
            product['temporalBaseline'] = 0
        else:
            start = dateparser.parse(product['startTime'])
            product['temporalBaseline'] = (start - master_start).days
    return stack

def offset_perpendicular_baselines(master, stack):
    for product in stack:
        if product['granuleName'] == master:
            master_offset = float(product['insarBaseline'])
            break
    for product in stack:
        if product['granuleName'] == master:
            product['perpendicularBaseline'] = 0
        else:
            product['perpendicularBaseline'] = float(product['insarBaseline']) - master_offset
    return stack

def calculate_perpendicular_baselines(master, stack):
    # totally faking perpendicular baseline data for the moment, come at me bro
    for product in stack:
        random.seed(product['granuleName']) # lol
        product['perpendicularBaseline'] = 0 if product['granuleName'] == master else random.randrange(-500, 500)
