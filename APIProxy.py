from flask import Response
import requests
import logging
from CMRTranslate import translators
import urls

logging.getLogger(__name__).addHandler(logging.NullHandler())

class APIProxyQuery:
    
    def __init__(self, request):
        self.request = request  # store the incoming request
        
        # currently supported input params
        self.cmr_params = [
            'output',
            'granule_list'
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
            'provider': 'ASF'
        }
        
        # use specified output format or default metalink
        output = 'metalink'
        if self.request.values['output']:
            output = self.request.values['output'].lower()
        if output not in translators.keys():
            output = 'metalink'
        
        # translate supported params into CMR query
        if self.request.values['granule_list']:
            params['readable_granule_name[]'] = self.request.values['granule_list'].split(',')
        
        # run the query, return the translated results
        r = requests.post(urls.cmr_api, data=params)
        text = translators[output](r)
        return Response(text, r.status_code, r.headers.items())

