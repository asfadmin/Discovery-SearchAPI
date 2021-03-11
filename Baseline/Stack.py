import dateparser
from CMR.Translate import translate_params, input_fixer
from CMR.Query import CMRQuery
from .Calc import calculate_perpendicular_baselines

precalc_datasets = ['AL', 'R1', 'E1', 'E2', 'J1']

def get_stack(master, req_fields=None, product_type=None):
    warnings = None

    try:
        stack_params = get_stack_params(master, product_type=product_type)
    except ValueError as e:
        raise e

    req_fields.extend([
        'granuleName',
        'startTime'])
    if get_platform(master) in precalc_datasets:
        req_fields.append('insarBaseline')
    elif get_platform(master) in ['S1']:
        req_fields.extend([
            'ascendingNodeTime',
            'centerLat',
            'centerLon',
            'stateVectors',
            'stopTime'
        ])

    stack = query_stack(stack_params, req_fields)

    if len(stack) <= 0:
        raise ValueError('No products found matching stack parameters')

    master, stack, warnings = check_master(master, stack)

    stack = calculate_temporal_baselines(master, stack)

    if get_platform(master) in precalc_datasets:
        stack = offset_perpendicular_baselines(master, stack)
    else:
        stack = calculate_perpendicular_baselines(master, stack)

    return stack, warnings

def get_stack_params(master, product_type=None):
    params = {'granule_list': master}
    if product_type is not None:
        params['processingLevel'] = product_type
    params,_,_ = translate_params(params)
    req_fields = [
        'processingLevel'
    ]
    if get_platform(master) in precalc_datasets:
        req_fields.extend([
            'insarGrouping'
        ])
    elif get_platform(master) in ['S1']:
        req_fields.extend([
            'beamMode',
            'centerLat',
            'centerLon',
            'flightDirection',
            'lookDirection',
            'platform',
            'polarization',
            'relativeOrbit'
        ])
    query = CMRQuery(
        req_fields,
        params=dict(params)
    )
    master_results = [product for product in query.get_results()]
    if len(master_results) <= 0:
        raise ValueError(f'Requested master not found, or no {product_type} product is available: {master}')

    stack_params = {}
    if product_type is not None:
        stack_params['processingLevel'] = product_type

    #shortcut the stacking for legacy datasets with precalculated stacks and baselines
    if get_platform(master) in precalc_datasets:
        if master_results[0]['insarGrouping'] is not None and master_results[0]['insarGrouping'] not in ['NA', 0, '0']:
            stack_params['insarstackid'] = master_results[0]['insarGrouping']
            return stack_params
        else:
            # if it's a precalc stack with no stack ID, we gotta bail because we don't have state vectors to fall back on
            raise ValueError(f'Requested master did not have a baseline stack ID: {master}')

    # build a stack from scratch if it's a non-precalc dataset with state vectors
    if get_platform(master) in ['S1']:
        stack_params['platform'] = get_platform(master)
        stack_params['beamMode'] = master_results[0]['beamMode']
        stack_params['flightDirection'] = master_results[0]['flightDirection']
        stack_params['lookDirection'] = master_results[0]['lookDirection']
        stack_params['relativeorbit'] = master_results[0]['relativeOrbit'] # path
        stack_params['polarization'] = master_results[0]['polarization']
        if stack_params['polarization'] in ['HH', 'HH+HV']:
            stack_params['polarization'] = 'HH,HH+HV'
        elif stack_params['polarization'] in ['VV', 'VV+VH']:
            stack_params['polarization'] = 'VV,VV+VH'
        stack_params['point'] = f"{master_results[0]['centerLon']},{master_results[0]['centerLat']}" # flexible alternative to frame

    return stack_params

def query_stack(params, req_fields):
    params,_,_ = translate_params(params)
    params = input_fixer(params)
    query = CMRQuery(
        req_fields,
        params=dict(params)
    )
    return [product for product in query.get_results()]

def valid_state_vectors(product):
    if product is None:
        raise ValueError(f'Attempting to check state vectors on None, this is fatal')
    if None in [product['sv_t_pos_pre'], product['sv_t_pos_post'], product['sv_pos_pre'], product['sv_pos_post']]:
        return False
    return True

def find_new_master(stack):
    for product in stack:
        if valid_state_vectors(product):
            return product['granuleName']
    return None

def check_master(master, stack):
    warnings = None
    if master not in [product['granuleName'] for product in stack]: # Somehow the reference we built the stack from is missing?! Just pick one
        master = stack[0]['granuleName']
        warnings = [{'NEW_MASTER': 'A new reference had to be selected in order to calculate baseline values.'}]

    for product in stack:
        if product['granuleName'] == master:
            master_product = product
    if not valid_state_vectors(master_product): # the reference might be missing state vectors, pick a valid reference, replace above warning if it also happened
        master = find_new_master(stack)
        if master is None:
            raise ValueError(f'No valid state vectors on any scenes in stack, this is fatal')
        warnings = [{'NEW_MASTER': 'A new reference had to be selected in order to calculate baseline values.'}]

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
            product['perpendicularBaseline'] = round(float(product['insarBaseline']) - master_offset)
    return stack
