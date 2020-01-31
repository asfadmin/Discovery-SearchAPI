import json
from datetime import datetime

from flask import Response, make_response, stream_with_context

import api_headers
import logging
from CMR.Query import CMRQuery
from CMR.Translate import translate_params, input_fixer
from CMR.Output import output_translators
from CMR.Exceptions import CMRError
from Analytics import analytics_events


class APIProxyQuery:

    def __init__(self, request):
        self.request = request
        self.cmr_params = {}
        self.output = 'metalink'
        self.max_results = None

    def get_response(self):
        self.post_analytics()

        validated = self.can_use_cmr()
        if validated is not True:
            return self.validation_error(validated)

        try:
            return self.cmr_query()
        except CMRError as e:
            return self.cmr_error(e)

    def post_analytics(self):
        events = [{'ec': 'Param', 'ea': v} for v in self.request.values]
        events.append({
            'ec': 'Param List',
            'ea': ', '.join(sorted([p.lower() for p in self.request.values]))
        })

        analytics_events(events=events)

    def can_use_cmr(self):
        try:
            self.check_has_search_params()
            self.check_and_set_cmr_params()
        except ValueError as e:
            logging.debug(f'ValueError: {e}')
            return e

        return True

    def check_has_search_params(self):
        non_searchable_param = ['output', 'maxresults', 'pagesize']
        searchables = [
            v for v in self.request.values if v not in non_searchable_param
        ]

        if len(searchables) <= 0:
            raise ValueError(
                'No searchable parameters specified, queries must include'
                ' parameters besides output= and maxresults='
            )

    def check_and_set_cmr_params(self):
        self.cmr_params, self.output, self.max_results = \
            translate_params(self.request.values)

        self.cmr_params = input_fixer(self.cmr_params)

    def cmr_query(self):
        logging.debug(f'Handle query from {self.request.access_route[-1]}')
        maxResults = self.max_results

        if is_max_results_with_json_output(maxResults, self.output):
            maxResults += 1

        q = CMRQuery(
            params=dict(self.cmr_params),
            output=self.output,
            max_results=maxResults,
            analytics=True
        )

        if self.output == 'count':
            return make_response(f'{q.get_count()}\n')

        translators = output_translators()

        translator, mimetype, suffix = translators \
            .get(self.output, translators['metalink'])

        filename = make_filename(suffix)
        d = api_headers.base(mimetype)
        d.add('Content-Disposition', 'attachment', filename=filename)

        stream = stream_with_context(translator(q.get_results))

        return Response(stream, headers=d)

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


def is_max_results_with_json_output(maxResults, output):
    '''
    This is absolutely the darndest thing. Something about streaming json AND having maxresults
    set leads to truncating the last result. If maxresults is not set, no truncation happens.
    This only affects json-based formats, all others work fine with or without maxresults.
    This is an admittedly kludgey workaround but I just can't seem to pinpoint the issue yet.
    '''

    return (
        maxResults is not None and
        output.lower() in ['json', 'jsonlite', 'geojson']
    )


def make_filename(suffix):
    return 'asf-datapool-results-{0}.{1}'.format(
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
        suffix
    )
