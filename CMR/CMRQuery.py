import urls
import requests
from flask import Response, make_response
import logging
from CMR.CMRTranslate import translators, parse_cmr_response
from Analytics import post_analytics

class CMRQuery:
    
    def __init__(self, params=None, max_results=None, output='metalink'):
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
                post_analytics(r, 'Proxy Error', 'CMR API {0}'.format(r.status_code))
                return Response(r.text, r.status_code, r.header_items())
        
            hits = int(r.headers['CMR-hits'])
            return make_response('{0}'.format(hits))
        
        if self.output == 'echo10': #truncate echo10 output to 1 page
            self.max_results = min(self.max_results, self.params['page_size'])
            
        subq = CMRSubQuery(params=self.params, max_results=self.max_results)
        results = subq.get_results()
        
        # trim the results if needed
        if self.max_results is not None and len(results) > self.max_results:
            logging.debug('trimming total results from {0} to {1}'.format(len(results), self.max_results))
            results = results[0:self.max_results]
        return make_response(translators.get(self.output, translators['metalink'])(results))

class CMRSubQuery:
    
    def __init__(self, params, max_results=None):
        self.params = params
        self.max_results = max_results
        logging.debug('new CMRSubQuery object ready to go')
    
    def get_results(self):
        logging.debug('fetching subquery results')
        
        r = requests.post(urls.cmr_api, data=self.params)
        
        # forward anything other than a 200
        if r.status_code != 200:
            return [] # do something wiser here
            
        hits = int(r.headers['CMR-hits'])
        sid = r.headers['CMR-Scroll-Id']
        
        segment = parse_cmr_response(r)
        results = []
            
        # fetch multiple pages of results if needed
        while True:
            results.extend(segment)
            logging.debug('fetched {0}/{1}'.format(len(results), min(hits, self.max_results)))
            if len(segment) <= 0 or (self.max_results is not None and len(results) >= self.max_results):
                break
            r = requests.post(urls.cmr_api, data=self.params, headers={'CMR-Scroll-Id': sid})
            segment = parse_cmr_response(r)
        
        # trim the results if needed
        if self.max_results is not None and len(results) > self.max_results:
            logging.debug('trimming subquery results from {0} to {1}'.format(len(results), self.max_results))
            results = results[0:self.max_results]
        
        return results