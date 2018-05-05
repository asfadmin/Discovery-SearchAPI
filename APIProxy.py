from flask import Response
import requests
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

class APIProxyQuery:
    
    def __init__(self, request):
        self.request = request  # store the incoming request
        self.asf_api_url = 'https://api.daac.asf.alaska.edu/services/search/param'
        self.cmr_api_url = 'https://cmr.earthdata.nasa.gov/search/granules.echo10'
        
        self.cmr_params = [
            'output',
            'granule_list'
        ]
        
    def can_use_cmr(self):
        params = self.request.values.keys()
        if set(params) <= set(self.cmr_params):
            return True
        return False
    
    def get_response(self):
        if self.can_use_cmr():
            logging.debug('get_response(): using CMR backend')
            return self.query_cmr()
        logging.debug('get_response(): using ASF backend')
        return self.query_asf()

    def query_asf(self):
        logging.info('API passthrough from {0}'.format(self.request.access_route[-1]))
        if self.request.method == 'GET':
            param_string = 'api_proxy=1&{0}'.format(self.request.query_string.decode('utf-8'))
            r = requests.get('{0}?{1}'.format(self.asf_api_url, param_string))
        elif self.request.method == 'POST':
            params = self.request.form
            params['api_proxy'] = 1
            param_string = '&'.join(list(map(lambda p: '{0}={1}'.format(p, params[p]), params)))
            r = requests.post(self.asf_api_url, data=self.request.form)
        if r.status_code != 200:
            logging.warning('Received status_code {0} from ASF API with params {1}'.format(r.status_code, param_string))
        return Response(r.text, r.status_code, r.headers.items())
    
    def query_cmr(self):
        logging.info('CMR translation from {0}'.format(self.request.access_route[-1]))
        params = {
            'provider': 'ASF'
        }
        if self.request.values['granule_list']:
            params['readable_granule_name[]'] = self.request.values['granule_list'].split(',')
        r = requests.post(self.cmr_api_url, data=params)
        return Response(r.text, r.status_code, r.headers.items())
