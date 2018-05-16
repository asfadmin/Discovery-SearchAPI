import requests
from flask import make_response
from math import ceil
from itertools import product
import logging
from CMR.CMRTranslate import output_translators, parse_cmr_response, input_map, input_fixer
from Analytics import post_analytics
from asf_env import get_config
from pprint import pprint

class CMRQuery:
    
    def __init__(self, params=None, max_results=None, output='metalink'):
        self.extra_params = {'provider': 'ASF', # always limit the results to ASF as the provider
                             'page_size': 2000, # max page size by default
                             'scroll': 'true',  # used for fetching multiple page_size
                             'options[temporal][and]': 'true', # Makes handling date ranges easier
                             #'options[attribute][pattern]': 'true' # Handy for flight direction & look direction
                             }
        
        self.params = input_fixer(params)
        self.max_results = max_results
        self.output = output

        if self.max_results is not None and self.max_results < self.extra_params['page_size']: # minimize data transfer on small max_results
            self.extra_params['page_size'] = self.max_results
        
        logging.debug('Building subqueries')
        self.query_list = self.get_query_list(self.params)
        self.sub_queries = [CMRSubQuery(params=q, max_results=self.max_results, count=True if self.output == 'count' else False) for q in self.query_list]
        logging.debug('{0} subqueries ready to go'.format(len(self.sub_queries)))
        
        logging.debug('new CMRQuery object ready to go')
    
    def run_sub_query(self, n):
        logging.debug('Dispatching subquery {0}'.format(n))
        return self.sub_queries[n].get_results()
        
    # Use the cartesian product of all the list parameters to determine subqueries
    def get_query_list(self, params):
        # First we have to get the params into a form itertools.product() understands
        listed_params = []
        for k in params.keys():
            plist = []
            if isinstance(params[k], list):
                for l in params[k]:
                    if isinstance(l, list):
                        plist.append({input_map()[k][0]: input_map()[k][1].format(','.join(['{0}'.format(t) for t in l]))})
                    else:
                        plist.append({input_map()[k][0]: input_map()[k][1].format(l)})
                listed_params.append(plist)
            else:
                listed_params.append([{input_map()[k][0]: input_map()[k][1].format(params[k])}])
        # Get the actual cartesian product
        query_list = list(product(*listed_params))
        # Clean up the query list so CMRSubQuery understands it
        final_query_list = []
        for q in query_list:
            params = {}
            for p in q:
                for k in p.keys():
                    params[k] = p[k]
            params.update(self.extra_params)
            final_query_list.append(params)
        logging.debug('=======')
        pprint(final_query_list)
        return final_query_list
    
    def get_results(self):
        
        # minimize data transfer if all we need is the hits header
        if self.output == 'count':
            logging.debug('Count query, doing this the quick way')
            total_hits = 0
            for sq in self.sub_queries:
                res = sq.get_results()
                if isinstance(res, int):
                    total_hits += res
                else:
                    logging.warning('Non-200 response from CMR, forwarding to client')
                    return make_response(res)
            return make_response('{0}'.format(total_hits))
            
        if self.output == 'echo10': #truncate echo10 output to 1st page of 1st subquery
            logging.debug('echo10 output, truncating to page 1 of query 1')
            self.max_results = min(self.max_results, self.extra_params['page_size'])
            self.query_list = [self.query_list[0]]
        
        results = []
        for subq in self.sub_queries:
            results.extend(subq.get_results())
            if len(results) >= self.max_results:
                break
        logging.debug('Result length: {0}'.format(len(results)))
        
        # trim the results if needed
        if self.max_results is not None and len(results) > self.max_results:
            logging.debug('Trimming total results from {0} to {1}'.format(len(results), self.max_results))
            results = results[0:self.max_results]
        return make_response(output_translators().get(self.output, output_translators()['metalink'])(results))

class CMRSubQuery:
    
    def __init__(self, params, max_results=1000000, mp_pool_size=1, count=False):
        self.params = params
        self.max_results = max_results if max_results is not None else 1000000
        self.sid = None
        self.hits = 0
        self.results = []
        self.mp_pool_size = mp_pool_size
        self.count = count
        logging.debug('new CMRSubQuery object ready to go')
        logging.debug(self.params)
    
    def get_results(self):
        s = requests.Session()
        
        logging.debug('Fetching head')
        r = s.head(get_config()['cmr_api'], data=self.params, headers={'Client-Id': 'vertex_asf'})
        
        post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}])
        # forward anything other than a 200
        if r.status_code != 200:
            logging.debug('Non-200 response from CMR')
            logging.debug(r.text)
            return r
        
        if self.count:
            return int(r.headers['CMR-hits'])
            
        self.hits = int(r.headers['CMR-hits'])
        if self.max_results > self.hits:
            self.max_results = self.hits
        self.sid = r.headers['CMR-Scroll-Id']
        s.headers.update({'CMR-Scroll-Id': self.sid})
        logging.debug('CMR reported {0} hits for session {1}'.format(self.hits, self.sid))
        
        #self.results = parse_cmr_response(r)
        
        # enumerate additional pages out to hit count or max_results, whichever is fewer (excluding first page)
        pages = []
        pages.extend(range(0, int(min(ceil(float(self.hits) / float(self.params['page_size'])), ceil(float(self.max_results) / float(self.params['page_size']))))))
        logging.debug('preparing to fetch {0} pages'.format(len(pages)))
        
        # fetch multiple pages of results if needed
        for p in pages:
            self.results.extend(self.get_page(p, s))
        logging.debug('done fetching results: got {0}/{1}'.format(len(self.results), self.hits))
        
        # trim the results if needed
        if self.max_results is not None and len(self.results) > self.max_results:
            logging.debug('trimming subquery results from {0} to {1}'.format(len(self.results), self.max_results))
            self.results = self.results[0:self.max_results]
        
        return self.results
    
    def get_page(self, p, s):
        logging.debug('Fetching page {0}'.format(p))
        r = s.get(get_config()['cmr_api'], data=self.params, headers={'CMR-Scroll-Id': self.sid, 'Client-Id': 'vertex_asf'})
        post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}])
        if r.status_code != 200:
            logging.error('Bad news bears! CMR said {0} on session {1}'.format(r.status_code, self.sid))
        
        results = parse_cmr_response(r)
        logging.debug('Fetched page {0}, {1} results'.format(p + 1, len(results)))
        return results
        