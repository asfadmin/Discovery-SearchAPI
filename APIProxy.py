from flask import Response, make_response
import requests
import logging
from datetime import datetime
from CMR.Query import CMRQuery
from CMR.Translate import translate_params, input_fixer, output_translators
from CMR.Exceptions import CMRError
from Analytics import post_analytics
from asf_env import get_config

class APIProxyQuery:
    
    def __init__(self, request):
        self.request = request  # store the incoming request
        self.cmr_params = {}
        self.output = 'metalink'
        self.max_results = None
        
    def can_use_cmr(self):
        # make sure the provided params are a subset of the CMR-supported params and have compatible values
        try:
            self.cmr_params, self.output, self.max_results = translate_params(self.request.values)
            self.cmr_params = input_fixer(self.cmr_params)
        except ValueError as e: # didn't parse, pass it to the legacy API for now
            logging.debug('ValueError: {0}'.format(e))
            return False
        return True
    
    def get_response(self):
        # pick a backend and go!
        events = [{'ec': 'Param', 'ea': v} for v in self.request.values]
        events.append({'ec': 'Param List', 'ea': ', '.join(sorted([p.lower() for p in self.request.values]))})
        if self.can_use_cmr():
            logging.debug('get_response(): using CMR backend')
            events.append({'ec': 'Proxy Search', 'ea': 'CMR'})
            post_analytics(pageview=True, events=events)
            try:
                logging.debug('Using CMR as backend, from {0}'.format(self.request.access_route[-1]))
                q = CMRQuery(params=self.cmr_params, output=self.output, max_results=self.max_results)
                results = q.get_results()
                (translator, mimetype, suffix) = output_translators().get(self.output, output_translators()['metalink'])
                filename = 'asf-datapool-results-{0}.{1}'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), suffix)
                response = make_response(translator(results))
                response.headers.set('Content-Type', mimetype)
                response.headers.set('Content-Disposition', 'attachment', filename=filename)
                return response
            except CMRError as e:
                return make_response('A CMR error has occured: {0}'.format(e))
        else:
            logging.debug('Can not use CMR, returning HTTP 400')
            return Response('', 400)
