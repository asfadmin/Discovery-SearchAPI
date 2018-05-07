from flask import Response, make_response
import requests
import logging
from CMRTranslate import translators, parse_cmr_xml
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
            'page_size': 1000,
            'scroll': 'true'
        }
        
        # use specified output format or default metalink
        output = 'metalink'
        if 'output' in self.request.values:
            output = self.request.values['output'].lower()
        
        # translate supported params into CMR query
        if 'granule_list' in self.request.values:
            params['readable_granule_name[]'] = self.request.values['granule_list'].split(',')
        if 'polygon' in self.request.values:
            params['polygon'] = self.request.values['polygon']
        
        # for later    
        #if 'platform' in self.request.values:
        #    params['platform[]'] = ['string,ASF_PLATFORM,{0}'.format(translate_platform(p)) for p in self.request.values['platform'].split(',')]
        #    logging.debug(params['platform[]'])
        
        # run the query, return the translated results
        r = requests.post(urls.cmr_api, data=params)
        session_id = r.headers['CMR-Scroll-Id']
        hits = int(r.headers['CMR-hits'])
        max_results = hits
        if 'maxresults' in self.request.values:
            max_results = int(self.request.values['maxresults'])
        if r.status_code == 200:
            if output == 'echo10':
                results = r.text
            else:
                results = parse_cmr_xml(r.text)
            if hits > params['page_size']:
                for n in range(hits // params['page_size']): # parallelize this!!
                    if n * params['page_size'] > max_results:
                        break
                    if output == 'echo10':
                        results += r.text
                    else:
                        results.extend(parse_cmr_xml(requests.post(urls.cmr_api, data=params, headers={'CMR-Scroll-Id': session_id}).text))
                    logging.debug('scrolled results downloaded for session {0}: {1}/{2}'.format(session_id, len(results), max_results))
            if output != 'echo10': # don't bother trimming if the output is echo10, it's close enough
                results = results[0:max_results] # trim off any excess from the last page
            text = translators.get(output, translators['metalink'])(results)
            return make_response(text)
        else:
            text = r.text
        return Response(text, r.status_code, r.headers.items())

