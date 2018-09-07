from itertools import product
import logging
from CMR.Translate import input_map
from CMR.SubQuery import CMRSubQuery

class CMRQuery:
    
    def __init__(self, params=None, max_results=None, output='metalink'):
        self.extra_params = {'provider': 'ASF', # always limit the results to ASF as the provider
                             'page_size': 100, # max page size by default
                             'scroll': 'true',  # used for fetching multiple page_size
                             'options[temporal][and]': 'true', # Makes handling date ranges easier
                             'sort_key[]': '-end_date', # Sort CMR results, but we also need to post-sort
                             #'options[attribute][pattern]': 'true' # Handy for flight direction & look direction
                             }
        
        self.params = params
        self.max_results = max_results
        self.output = output
        
        self.result_counter = 0

        if self.max_results is not None and self.max_results < self.extra_params['page_size']: # minimize data transfer on small max_results
            self.extra_params['page_size'] = self.max_results
        
        logging.debug('Building subqueries using params:')
        logging.debug(self.params)
        logging.debug('output: {0}'.format(self.output))
        logging.debug('maxresults: {0}'.format(self.max_results))
        self.query_list = self.get_query_list(self.params)
        self.sub_queries = [CMRSubQuery(params=list(q), extra_params=self.extra_params) for q in self.query_list]
        logging.debug('{0} subqueries ready to go'.format(len(self.sub_queries)))
        
        logging.debug('new CMRQuery object ready to go')
    
    # Not currently used, intended to act as a dispatcher for threading
    def run_sub_query(self, n):
        logging.debug('Dispatching subquery {0}'.format(n))
        return self.sub_queries[n].get_results()
        
    # Use the cartesian product of all the list parameters to determine subqueries
    def get_query_list(self, params):
        # First we have to get the params into a form itertools.product() understands
        listed_params = []
        for k in params:
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
        return query_list
    
    def get_count(self):
        total_hits = 0
        for sq in self.sub_queries:
            total_hits += sq.get_count()
        return total_hits
    
    def get_results(self):
        for n, subq in enumerate(self.sub_queries):
            logging.debug('Running subquery {0}'.format(n+1))
            # taking a page at a time from each subquery, yield one result at a time until we max out
            for r in subq.get_results():
                self.result_counter += len(r)
                if self.max_results is not None and self.result_counter > self.max_results:
                    logging.debug('Trimming total results from {0} to {1}'.format(self.result_counter, self.max_results))
                    r = r[0:-(self.result_counter - self.max_results)]
                    for i in r:
                        yield i
                    return
                else:
                    for i in r:
                        yield i

        logging.debug('Result length: {0}'.format(self.result_counter))
        return


        