from flask import Response, make_response
import requests
import logging
from CMR.CMRQuery import CMRQuery
from CMR.CMRTranslate import translate_params
from Analytics import post_analytics
from asf_env import get_config

class APIProxyQuery:
    
    def __init__(self, request):
        self.request = request  # store the incoming request
        self.cmr_params = {}
        self.output = 'metalink'
        self.max_results = None
        
    def can_use_cmr(self):
        # make sure the provided params are a subset of the CMR-supported params
        supported = False
        try:
            self.cmr_params, self.output, self.max_results = translate_params(self.request.values)
            supported = True
        except ValueError: # didn't parse, pass it to the legacy API for now
            pass
        return supported
    
    def get_response(self):
        # pick a backend and go!
        events = [{'ec': 'Param', 'ea': v} for v in self.request.values.keys()]
        if self.can_use_cmr():
            logging.debug('get_response(): using CMR backend')
            events.append({'ec': 'Proxy Search', 'ea': 'CMR'})
            post_analytics(pageview=True, events=events)
            return self.query_cmr()
        logging.debug('get_response(): using ASF backend')
        events.append({'ec': 'Proxy Search', 'ea': 'Legacy'})
        post_analytics(pageview=True, events=events)
        return self.query_asf()
        
    # ASF API backend query
    def query_asf(self):
        # preserve GET/POST approach when querying ASF API
        logging.info('API passthrough from {0}'.format(self.request.access_route[-1]))
        if self.request.method == 'GET':
            param_string = 'api_proxy=1&{0}'.format(self.request.query_string.decode('utf-8'))
            r = requests.get('{0}?{1}'.format(get_config()['asf_api'], param_string))
        else: # self.request.method == 'POST':
            params = self.request.form
            params['api_proxy'] = 1
            param_string = '&'.join(list(map(lambda p: '{0}={1}'.format(p, params[p]), params)))
            r = requests.post(get_config()['asf_api'], data=self.request.form)
        post_analytics(pageview=False, events=[{'ec': 'ASF API Status', 'ea': r.status_code}])
        if r.status_code != 200:
            logging.warning('Received status_code {0} from ASF API with params {1}'.format(r.status_code, param_string))
            return Response(r.text, r.status_code, r.headers.items())
        return make_response(r.text)
        
    # CMR backend query
    def query_cmr(self):
        logging.info('CMR translation from {0}'.format(self.request.access_route[-1]))
        # always limit the results to ASF as the provider
        self.cmr_params['provider'] = 'ASF'
        self.cmr_params['page_size'] = 2000 # max page size by default
        self.cmr_params['scroll'] = 'true'
        
        if self.max_results is not None and self.max_results < self.cmr_params['page_size']: # minimize data transfer on small max_results
            self.cmr_params['page_size'] = self.max_results
        
        q = CMRQuery(params=self.cmr_params, output=self.output, max_results=self.max_results)
        r = q.get_results()
        
        return r
