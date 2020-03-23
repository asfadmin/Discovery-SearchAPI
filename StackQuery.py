import logging
import json

from flask import Response, make_response
from datetime import datetime

import api_headers
from CMR.Input import parse_string
from Baseline import get_stack
from asf_env import get_config


class APIStackQuery:

    def __init__(self, request):
        self.request = request
        self.params = None # populated by self.validate()

    def get_response(self):
        logging.debug(self.request.values)
        try:
            self.validate()
            stack = get_stack(self.params['master'])
            resp = json.dumps(stack)
        except ValueError as e:
            return self.validation_error(e)

        resp = json.dumps(stack)

        filename = make_filename('json')
        d = api_headers.base('application/json; charset=utf-8')
        d.add('Content-Disposition', 'attachment', filename=filename)

        return Response(resp, headers=d)

    def validate(self):
        valid_params = ['master', 'output']
        if get_config()['flexible_maturity']:
            valid_params.append('maturity')

        params = {}
        try:
            for k in self.request.values:
                key = k.lower()
                val = self.request.values[k]
                if key not in valid_params:
                    raise ValueError(f'Unrecognized parameter: {key}')
                parse_string(val)
                params[key] = val
            self.params = params
        except ValueError as e:
            logging.debug(f'ValueError: {e}')
            raise e

    def validation_error(self, error):
        logging.debug('Malformed query, returning HTTP 400')
        logging.debug(self.request.values)

        d = api_headers.base(mimetype='application/json')

        resp = json.dumps({
            'error': {
                'type': 'VALIDATION_ERROR',
                'report': f'Validation Error: {error}'
            }
        }, sort_keys=True, indent=4)

        return Response(resp, 400, headers=d)

    def cmr_error(self, e):
        return make_response(f'A CMR error has occured: {e}')

def make_filename(suffix):
    return 'asf-datapool-results-{0}.{1}'.format(
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
        suffix
    )
