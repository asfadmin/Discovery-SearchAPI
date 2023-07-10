import dateparser
from SearchAPI.CMR.Translate import translate_params, input_fixer
from SearchAPI.CMR.Query import CMRQuery
from .Calc import calculate_perpendicular_baselines

precalc_datasets = ['AL', 'R1', 'E1', 'E2', 'J1']

def get_stack(reference, req_fields=None, product_type=None):
    warnings = None

    stack_params, req_fields = build_stack_params(reference, req_fields, product_type)

    stack = query_stack(stack_params, req_fields)

    if len(stack) <= 0:
        raise ValueError('No products found matching stack parameters')

    reference, stack, warnings = check_reference(reference, stack)

    stack = calculate_temporal_baselines(reference, stack)

    if get_platform(reference) in precalc_datasets:
        stack = offset_perpendicular_baselines(reference, stack)
    else:
        stack = calculate_perpendicular_baselines(reference, stack)

    return stack, warnings

def build_stack_params(reference, req_fields=None, product_type=None):
    try:
        stack_params = get_stack_params(reference, product_type=product_type)
    except ValueError as e:
        raise e

    req_fields.extend([
        'granuleName',
        'startTime'])
    if get_platform(reference) in precalc_datasets:
        req_fields.append('insarBaseline')
    elif get_platform(reference) in ['S1']:
        req_fields.extend([
            'ascendingNodeTime',
            'centerLat',
            'centerLon',
            'stateVectors',
            'stopTime'
        ])
    
    return stack_params, req_fields

def get_stack_params(reference, product_type=None):
    params = {'granule_list': reference}
    if product_type is not None:
        params['processingLevel'] = product_type
    params,_,_ = translate_params(params)
    req_fields = [
        'processingLevel'
    ]
    if get_platform(reference) in precalc_datasets:
        req_fields.extend([
            'insarGrouping'
        ])
    elif get_platform(reference) in ['S1']:
        req_fields.extend([
            'beamMode',
            'centerLat',
            'centerLon',
            'flightDirection',
            'lookDirection',
            'platform',
            'polarization',
            'relativeOrbit',
            'fullBurstID'
        ])
    query = CMRQuery(
        req_fields,
        params=dict(params)
    )
    reference_results = [product for product in query.get_results()]
    if len(reference_results) <= 0:
        raise ValueError(f'Requested reference not found, or no {product_type} product is available: {reference}')

    stack_params = {}
    if product_type is not None:
        stack_params['processingLevel'] = product_type

    #shortcut the stacking for legacy datasets with precalculated stacks and baselines
    if get_platform(reference) in precalc_datasets:
        if reference_results[0]['insarGrouping'] is not None and reference_results[0]['insarGrouping'] not in ['NA', 0, '0']:
            stack_params['insarstackid'] = reference_results[0]['insarGrouping']
            return stack_params
        else:
            # if it's a precalc stack with no stack ID, we gotta bail because we don't have state vectors to fall back on
            raise ValueError(f'Requested reference did not have a baseline stack ID: {reference}')

    # build a stack from scratch if it's a non-precalc dataset with state vectors
    
    if stack_params['processingLevel'] == 'BURST':
        stack_params['polarization'] = reference_results[0]['polarization']
        stack_params['fullBurstID'] = reference_results[0]['fullBurstID']
    elif get_platform(reference) in ['S1']:
        stack_params['platform'] = get_platform(reference)
        stack_params['beamMode'] = reference_results[0]['beamMode']
        stack_params['flightDirection'] = reference_results[0]['flightDirection']
        stack_params['relativeorbit'] = reference_results[0]['relativeOrbit'] # path

        stack_params['polarization'] = reference_results[0]['polarization']
        if stack_params['polarization'] in ['HH', 'HH+HV']:
            stack_params['polarization'] = 'HH,HH+HV'
        elif stack_params['polarization'] in ['VV', 'VV+VH']:
            stack_params['polarization'] = 'VV,VV+VH'

        stack_params['lookDirection'] = reference_results[0]['lookDirection']
        
        stack_params['point'] = f"{reference_results[0]['centerLon']},{reference_results[0]['centerLat']}" # flexible alternative to frame

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
        raise ValueError('Attempting to check state vectors on None, this is fatal')
    for key in ['sv_t_pos_pre', 'sv_t_pos_post', 'sv_pos_pre', 'sv_pos_post']:
        if key not in product or product[key] == None:
            return False
    return True

def find_new_reference(stack):
    for product in stack:
        if valid_state_vectors(product):
            return product['granuleName']
    return None

def check_reference(reference, stack):
    warnings = None
    if reference not in [product['granuleName'] for product in stack]: # Somehow the reference we built the stack from is missing?! Just pick one
        reference = stack[0]['granuleName']
        warnings = [{'NEW_REFERENCE': 'A new reference scene had to be selected in order to calculate baseline values.'}]

    for product in stack:
        if product['granuleName'] == reference:
            reference_product = product

    if get_platform(reference) in precalc_datasets:
            if 'insarBaseline' not in reference_product:
                raise ValueError('No baseline values available for precalculated dataset')
    else:
        if not valid_state_vectors(reference_product): # the reference might be missing state vectors, pick a valid reference, replace above warning if it also happened
            reference = find_new_reference(stack)
            if reference is None:
                raise ValueError('No valid state vectors on any scenes in stack, this is fatal')
            warnings = [{'NEW_REFERENCE': 'A new reference had to be selected in order to calculate baseline values.'}]

    return reference, stack, warnings

def get_platform(reference):
    return reference[0:2].upper()

def get_default_product_type(reference):
    if get_platform(reference) in ['AL']:
        return 'L1.1'
    if get_platform(reference) in ['R1', 'E1', 'E2', 'J1']:
        return 'L0'
    if get_platform(reference) in ['S1']:
        if reference.endswith('BURST'):
            return 'BURST'        
        return 'SLC'
    return None

def calculate_temporal_baselines(reference, stack):
    for product in stack:
        if product['granuleName'] == reference:
            reference_start = dateparser.parse(product['startTime'])
            break
    for product in stack:
        if product['granuleName'] == reference:
            product['temporalBaseline'] = 0
        else:
            start = dateparser.parse(product['startTime'])
            product['temporalBaseline'] = (start.date() - reference_start.date()).days
    return stack

def offset_perpendicular_baselines(reference, stack):
    for product in stack:
        if product['granuleName'] == reference:
            reference_offset = float(product['insarBaseline'])
            break
    for product in stack:
        if product['granuleName'] == reference:
            product['perpendicularBaseline'] = 0
        else:
            product['perpendicularBaseline'] = round(float(product['insarBaseline']) - reference_offset)
    return stack
