import json

from flask import Response, make_response
from datetime import datetime
import logging

import api_headers
from CMR.Input import parse_string
from CMR.Output import output_translators
from Baseline import get_stack, get_default_product_type


class APIStackQuery:

    def __init__(self, request):
        self.request = request
        self.params = None # populated by self.validate()

    def get_response(self):
        try:
            self.validate()
            if 'processinglevel' not in self.params:
                self.params['processinglevel'] = get_default_product_type(self.params['master'])
            if 'output' not in self.params:
                self.params['output'] = 'metalink'

            translators = output_translators()
            translator, mimetype, suffix, req_fields = translators.get(self.params['output'], translators['metalink'])

            is_count = self.params['output'].lower() == 'count'
            stack, warnings = get_stack(
                master=self.params['master'],
                req_fields=req_fields,
                product_type=self.params['processinglevel'])
            if is_count:
                return make_response(f'{len(stack)}\n')


            filename = make_filename(suffix)
            d = api_headers.base(mimetype)
            d.add('Content-Disposition', 'attachment', filename=filename)

            # yick
            def stack_generator():
                if stack is None:
                    return
                for product in stack:
                    yield product

            resp = ''.join(
                translator(stack_generator,
                    includeBaseline=True,
                    addendum={'warnings': warnings} if warnings is not None else None))

            return Response(resp, headers=d)

        except ValueError as e:
            return self.validation_error(e)

        resp = json.dumps(stack)

        filename = make_filename('json')
        d = api_headers.base('application/json; charset=utf-8')
        d.add('Content-Disposition', 'attachment', filename=filename)

        return Response(resp, headers=d)

    def validate(self):
        valid_params = ['master', 'output', 'processinglevel']

        params = {}
        try:
            for k in self.request.local_values:
                key = k.lower()
                val = self.request.local_values[k]
                if key not in valid_params:
                    raise ValueError(f'Unrecognized parameter: {key}')
                val = parse_string(val)
                params[key] = val
            if 'master' not in params:
                raise ValueError("Could not find 'master' in post request.")
            # If you try passing in multiple masters:
            if "," in str(params['master']):
                raise ValueError("Can only pass in one master granule.")
            self.params = params
        except ValueError as e:
            logging.debug(f'ValueError: {e}')
            raise e

    def validation_error(self, error):
        logging.debug('Malformed query, returning HTTP 400')
        logging.debug(self.request.local_values)

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
