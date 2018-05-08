from flask import Response
import requests
import logging
from CMR.CMRQuery import CMRQuery
from CMR.CMRTranslate import translate_params
import urls
from Analytics import post_analytics

class APIProxyQuery:
    
    def __init__(self, request):
        self.request = request  # store the incoming request
        self.cmr_params = {}
        
    def can_use_cmr(self):
        # make sure the provided params are a subset of the CMR-supported params
        supported = False
        try:
            self.cmr_params = translate_params(self.request.values)
            supported = True
        except ValueError:
            pass
        return supported
    
    def get_response(self):
        # pick a backend and go!
        logging.debug(self.can_use_cmr())
        if self.can_use_cmr():
            logging.debug('get_response(): using CMR backend')
            post_analytics(self.request, 'proxy', 'CMR')
            return self.query_cmr()
        logging.debug('get_response(): using ASF backend')
        post_analytics(self.request, 'proxy', 'Legacy')
        return self.query_asf()
        
    # ASF API backend query
    def query_asf(self):
        # preserve GET/POST approach when querying ASF API
        logging.info('API passthrough from {0}'.format(self.request.access_route[-1]))
        if self.request.method == 'GET':
            param_string = 'api_proxy=1&{0}'.format(self.request.query_string.decode('utf-8'))
            r = requests.get('{0}?{1}'.format(urls.asf_api, param_string))
        else: # self.request.method == 'POST':
            params = self.request.form
            params['api_proxy'] = 1
            param_string = '&'.join(list(map(lambda p: '{0}={1}'.format(p, params[p]), params)))
            r = requests.post(urls.asf_api, data=self.request.form)
        if r.status_code != 200:
            post_analytics(self.request, 'error', 'ASF API {0}'.format(r.status_code))
            logging.warning('Received status_code {0} from ASF API with params {1}'.format(r.status_code, param_string))
        return Response(r.text, r.status_code, r.headers.items())
        
    # CMR backend query
    def query_cmr(self):
        logging.info('CMR translation from {0}'.format(self.request.access_route[-1]))
        # always limit the results to ASF as the provider
        params = {
            'provider': 'ASF',
            'page_size': 2000, # max page size by default
            'scroll': 'true'
        }
        
        # handle a few special parameters that we support but won't be going to CMR
        max_results = None
        if 'maxresults' in self.request.values:
            max_results = int(self.request.values['maxresults'])
            if max_results < params['page_size']: # minimize data transfer
                params['page_size'] = max_results
        
        # use specified output format or default metalink
        output = 'metalink'
        if 'output' in self.request.values:
            output = self.request.values['output'].lower()
        
        q = CMRQuery(params=params, output=output, max_results=max_results)
        r = q.get_results()
        
        return r
