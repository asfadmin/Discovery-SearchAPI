from .input_map import input_map

from CMR.Output import output_translators


def translate_params(p):
    """
    Translate supported params into CMR params
    """
    params = {}

    for k in p:
        if k.lower() not in input_map():
            raise ValueError(f'Unsupported parameter: {k}')
        try:
            params[k.lower()] = input_map()[k.lower()][2](p[k])
        except ValueError as e:
            raise ValueError(f'{k}: {e}')

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
