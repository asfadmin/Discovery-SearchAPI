from flask import Response, make_response, stream_with_context
import api_headers
import logging
from datetime import datetime
from CMR.Query import CMRQuery
from CMR.Translate import translate_params, input_fixer
from CMR.Output import output_translators
from CMR.Exceptions import CMRError
from Analytics import post_analytics
from CacheQuery import run_threaded_caching_query

class APIProxyQuery:

    def __init__(self, request):
        self.request = request  # store the incoming request
        self.cmr_params = {}
        self.output = 'metalink'
        self.max_results = None

    def can_use_cmr(self):
        # make sure the provided params are a subset of the CMR-supported params and have compatible values
        try:
            self.cmr_params, self.output, self.max_results, self.page_size = translate_params(self.request.values)
            self.cmr_params = input_fixer(self.cmr_params)
        except ValueError as e: # didn't parse, pass it to the legacy API for now
            logging.debug('ValueError: {0}'.format(e))
            return False
        return True

    def get_response(self):
        events = [{'ec': 'Param', 'ea': v} for v in self.request.values]
        events.append({'ec': 'Param List', 'ea': ', '.join(sorted([p.lower() for p in self.request.values]))})
        if self.can_use_cmr():
            events.append({'ec': 'Proxy Search', 'ea': 'CMR'})
            post_analytics(pageview=True, events=events)
            try:
                logging.debug('Handling query from {0}'.format(self.request.access_route[-1]))
                maxResults = self.max_results

                if self.output == 'jsonlite':
                    maxResults = min(maxResults, self.page_size) \
                        if maxResults is not None \
                        else self.page_size

                q = CMRQuery(params=dict(self.cmr_params), output=self.output, max_results=maxResults, analytics=True)
                if(self.output == 'count'):
                    return(make_response(str(q.get_count())))
                (translator, mimetype, suffix) = output_translators().get(self.output, output_translators()['metalink'])
                filename = 'asf-datapool-results-{0}.{1}'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), suffix)
                d = api_headers.base(mimetype)
                d.add('Content-Disposition', 'attachment', filename=filename)
                if self.output == 'jsonlite':
                    # Fire off copy of same query in separate thread for caching purposes
                    cache_id = run_threaded_caching_query(CMRQuery(params=dict(self.cmr_params), output=self.output, max_results=self.max_results, analytics=False), self.page_size)
                    d.add('ASF-Cache-ID', cache_id)
                return Response(stream_with_context(translator(q.get_results)), headers=d)
            except CMRError as e:
                return make_response('A CMR error has occured: {0}'.format(e))
        else:
            logging.warning('Malformed query, returning HTTP 400')
            logging.warning(self.request.values)
            return Response('', 400)
