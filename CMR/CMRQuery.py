import urls
import requests
from flask import Response, make_response
from math import ceil
from multiprocessing import Pool
from time import sleep
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
    
    def __init__(self, params, max_results=1000000, mp_pool_size=1):
        self.params = params
        self.max_results = max_results if max_results is not None else 1000000
        self.sid = None
        self.hits = 0
        self.results = []
        self.mp_pool_size = mp_pool_size
        logging.debug('new CMRSubQuery object ready to go')
    
    def get_results(self):
        
        logging.debug('fetching page 0')
        r = requests.post(urls.cmr_api, data=self.params, headers={'Client-Id': 'vertex_asf'})
        
        # forward anything other than a 200
        if r.status_code != 200:
            return [] # do something wiser here
            
        self.hits = int(r.headers['CMR-hits'])
        if self.max_results > self.hits:
            self.max_results = self.hits
        self.sid = r.headers['CMR-Scroll-Id']
        logging.debug('CMR reported {0} hits for session {1}'.format(self.hits, self.sid))
        
        self.results = parse_cmr_response(r)
        
        # enumerate additional pages out to hit count or max_results, whichever is fewer (excluding first page)
        extra_pages = []
        extra_pages.extend(range(1, min(ceil(self.hits / self.params['page_size']), ceil(self.max_results / self.params['page_size']))))
        logging.debug('preparing to fetch {0} pages'.format(len(extra_pages)))
        # fetch multiple pages of results if needed
        result_pages = []
        with Pool(self.mp_pool_size) as p:
            result_pages.extend(p.map(self.get_page, extra_pages))
        for p in result_pages:
            self.results.extend(p)
        logging.debug('done fetching results: got {0}/{1}'.format(len(self.results), self.hits))
        
        # trim the results if needed
        if self.max_results is not None and len(self.results) > self.max_results:
            logging.debug('trimming subquery results from {0} to {1}'.format(len(self.results), self.max_results))
            self.results = self.results[0:self.max_results]
        
        return self.results
    
    def get_page(self, p):
        if p < self.mp_pool_size:
            sleep(p)
        logging.debug('fetching page {0}'.format(p))
        r = requests.post(urls.cmr_api, data=self.params, headers={'CMR-Scroll-Id': self.sid, 'Client-Id': 'vertex_asf'})
        if r.status_code != 200:
            logging.error('Bad news bears! CMR said {0} on session {1}'.format(r.status_code, self.sid))
        
        results = parse_cmr_response(r)
        logging.debug('fetched page {0}, {1} results'.format(p + 1, len(results)))
        return results
        