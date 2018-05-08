from flask import Response
import requests
import logging
from CMR.CMRQuery import CMRQuery
import urls

logging.getLogger(__name__).addHandler(logging.NullHandler())

class APIProxyQuery:
    
    def __init__(self, request):
        self.request = request  # store the incoming request
        
        # currently supported input params
        self.cmr_params = [
            'output',
            'granule_list',
            'polygon',
            #'platform'
            'maxresults'
        ]
        
    def can_use_cmr(self):
        # make sure the provided params are a subset of the CMR-supported params
        if set(self.request.values.keys()) <= set(self.cmr_params):
            return True
        return False
    
    def get_response(self):
        # pick a backend and go!
        if self.can_use_cmr():
            logging.debug('get_response(): using CMR backend')
            return self.query_cmr()
        logging.debug('get_response(): using ASF backend')
        return self.query_asf()
        
    # ASF API backend query
    def query_asf(self):
        # preserve GET/POST approach when querying ASF API
        logging.info('API passthrough from {0}'.format(self.request.access_route[-1]))
        if self.request.method == 'GET':
            param_string = 'api_proxy=1&{0}'.format(self.request.query_string.decode('utf-8'))
            r = requests.get('{0}?{1}'.format(urls.asf_api, param_string))
        elif self.request.method == 'POST':
            params = self.request.form
            params['api_proxy'] = 1
            param_string = '&'.join(list(map(lambda p: '{0}={1}'.format(p, params[p]), params)))
            r = requests.post(urls.asf_api, data=self.request.form)
        if r.status_code != 200:
            logging.warning('Received status_code {0} from ASF API with params {1}'.format(r.status_code, param_string))
        return Response(r.text, r.status_code, r.headers.items())
        
    # CMR backend query
    def query_cmr(self):
        logging.info('CMR translation from {0}'.format(self.request.access_route[-1]))
        # always limit the results to ASF as the provider
        params = {
            'provider': 'ASF',
            'page_size': 2000,
            'scroll': 'true'
        }
        
        # use specified output format or default metalink
        output = 'metalink'
        if 'output' in self.request.values:
            output = self.request.values['output'].lower()
        
        max_results = None
        if 'maxresults' in self.request.values:
            max_results = self.request.values['maxresults']
        
        # translate supported params into CMR params
        if 'granule_list' in self.request.values:
            params['readable_granule_name[]'] = self.request.values['granule_list'].split(',')
        if 'polygon' in self.request.values:
            params['polygon'] = self.request.values['polygon']
        
        q = CMRQuery(params=params, output=output, max_results=max_results)
        r = q.get_results()
        
        return r
