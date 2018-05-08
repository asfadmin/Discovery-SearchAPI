import urls
import requests
from flask import Response, make_response
import logging
from CMR.CMRTranslate import translators, parse_cmr_response

class CMRQuery:
    
    def __init__(self, params=None, max_results=None, output='metalink'):
        self.echo10_results = []
        self.params = params
        self.max_results = max_results
        self.output = output
        logging.debug('new CMRQuery object ready to go')
    
    def get_results(self):
        logging.debug('fetching query results')
        
        # minimize data transfer if all we need is the hits header
        if self.output == 'count':
            self.params['page_size'] = 1
        
        r = requests.post(urls.cmr_api, data=self.params)
        
        # forward anything other than a 200
        if r.status_code != 200:
            logging.warning('Non-200 response from CMR, forwarding to client')
            return Response(r.text, r.status_code, r.header_items())
        
        hits = int(r.headers['CMR-hits'])
        sid = r.headers['CMR-Scroll-Id']
        
        # intercept count option
        if self.output == 'count':
            return make_response(hits)
            
        results = parse_cmr_response(r)
            
        # fetch multiple pages of results if needed...don't bother if they want echo10 output
        if hits > self.params['page_size'] and self.max_results > self.params['page_size'] and self.output != 'echo10':
            while len(results) <= self.max_results:
                r = requests.post(urls.cmr_api, data=self.params, headers={'CMR-Scroll-Id': sid})
                results.extend(parse_cmr_response(r))
        
        # trim the results if needed
        if self.max_results is not None and len(results) >= self.max_results:
            logging.debug('trimming results from {0} to {1}'.format(len(results), self.max_results))
            results = results[0:self.max_results]
        return make_response(translators.get(self.output, translators['metalink'])(results))
        