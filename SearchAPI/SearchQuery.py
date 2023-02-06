from datetime import datetime
import logging
import json

from flask import Response, make_response, stream_with_context

import SearchAPI.api_headers as api_headers
from SearchAPI.CMR.Query import CMRQuery
from SearchAPI.CMR.Translate import translate_params, input_fixer
from SearchAPI.CMR.Output import output_translators
from SearchAPI.CMR.Exceptions import CMRError
from SearchAPI.Analytics import analytics_events


class APISearchQuery:

    def __init__(self, request, should_stream=True):
        self.request = request
        self.cmr_params = {}
        self.output = 'metalink'
        self.max_results = None
        self.should_stream = should_stream

    def get_response(self):
        logging.info(f"Query Strings: {self.request.local_values=}")
        validated = self.can_use_cmr()
        if validated is not True:
            return self.validation_error(validated)

        try:
            return self.cmr_query()
        except CMRError as e:
            return self.cmr_error(e)

    def post_analytics(self):
        events = [{'ec': 'Param', 'ea': v} for v in self.request.local_values]
        events.append({
            'ec': 'Param List',
            'ea': ', '.join(sorted([p.lower() for p in self.request.local_values]))
        })

        analytics_events(events=events)

    def can_use_cmr(self):
        try:
            self.check_has_search_params()
            self.check_and_set_cmr_params()
        except ValueError as e:
            logging.exception(f'ValueError: {e}')
            return e

        return True

    def check_has_search_params(self):
        non_searchable_param = ['output', 'maxresults', 'pagesize', 'maturity']
        list_param_exceptions = ['collections']
        
        searchables = [
            v for v in self.request.local_values if v.lower() not in [*non_searchable_param, *list_param_exceptions]
        ]

        if len(searchables) <= 0:
            raise ValueError(
                'No searchable parameters specified, queries must include'
                ' parameters besides output= and maxresults='
            )
        if 'granule_list' in searchables and len(searchables) > 1:
            raise ValueError(
                'granule_list may not be used in conjunction with other search parameters'
            )

        if 'product_list' in searchables and len(searchables) > 1:
            raise ValueError(
                'product_list may not be used in conjunction with other search parameters'
            )

    def check_and_set_cmr_params(self):
        self.cmr_params, self.output, self.max_results = \
            translate_params(self.request.local_values)

        self.cmr_params = input_fixer(self.cmr_params, 
                                      self.request.asf_config['cmr_base'] == 'https://cmr.earthdata.nasa.gov', 
                                      getattr(self.request, 'cmr_provider', 'ASF'))

    def cmr_query(self):
        logging.debug(f'Handle query from {self.request.access_route[-1]}')
        maxResults = self.max_results

        if is_max_results_with_json_output(maxResults, self.output):
            maxResults += 1

        translators = output_translators()
        translator, mimetype, suffix, req_fields = translators.get(self.output, translators['metalink'])

        query = CMRQuery(
            req_fields,
            params=dict(self.cmr_params),
            max_results=maxResults
        )

        if self.output == 'count':
            return make_response(f'{query.get_count()}\n')

        filename = make_filename(suffix)
        d = api_headers.base(mimetype)
        d.add('Content-Disposition', 'attachment', filename=filename)

        if self.should_stream:
            resp = stream_with_context(translator(query.get_results))
        else:
            resp = ''.join(translator(query.get_results))

        return Response(resp, headers=d, mimetype=mimetype)

    def validation_error(self, error):
        logging.debug('Malformed query, returning HTTP 400')
        logging.debug(self.request.local_values)

        mimetype='application/json'
        d = api_headers.base(mimetype=mimetype)

        resp = json.dumps({
            'error': {
                'type': 'VALIDATION_ERROR',
                'report': f'Validation Error: {error}'
            }
        }, sort_keys=True, indent=4)

        return Response(resp, 400, headers=d, mimetype=mimetype)

    def cmr_error(self, e):
        return make_response(f'A CMR error has occured: {e}')


def is_max_results_with_json_output(maxResults, output):
    '''
    This is absolutely the darndest thing. Something about streaming json AND having maxresults
    set leads to truncating the last result. If maxresults is not set, no truncation happens.
    This only affects json-based formats, all others work fine with or without maxresults.
    This is an admittedly kludgey workaround but I just can't seem to pinpoint the issue yet.
    '''

    return (
        maxResults is not None and
        output.lower() in ['json', 'jsonlite', 'geojson', 'jsonlite2', 'asf_search']
    )


def make_filename(suffix):
    return f'asf-datapool-results-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.{suffix}'
