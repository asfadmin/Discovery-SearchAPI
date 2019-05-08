from itertools import product
import logging
import time
from CMR.Translate import input_map
from CMR.SubQuery import CMRSubQuery

class CMRQuery:

    def __init__(self, params=None, max_results=None, output='metalink', analytics=True):
        self.extra_params = {'provider': 'ASF', # always limit the results to ASF as the provider
                             'page_size': 2000, # page size to request from CMR
                             'scroll': 'true',  # used for fetching multiple page_size
                             'options[temporal][and]': 'true', # Makes handling date ranges easier
                             'sort_key[]': '-end_date', # Sort CMR results, but this is partially defeated by the subquery system
                             'options[platform][ignore_case]': 'true'
                             }

        self.params = params
        self.max_results = max_results
        self.output = output
        self.analytics = analytics

        self.result_counter = 0
        self.cutoff_time = time.time() + 870 #14.5 minutes max

        if self.max_results is not None and self.max_results < self.extra_params['page_size']: # minimize data transfer on small max_results
            self.extra_params['page_size'] = self.max_results

        logging.debug('Building subqueries using params:')
        logging.debug(self.params)
        self.query_list = self.get_query_list(self.params)
        self.sub_queries = [CMRSubQuery(params=list(q), extra_params=self.extra_params, analytics=self.analytics) for q in self.query_list]
        logging.debug('{0} subqueries built'.format(len(self.sub_queries)))

        logging.debug('New CMRQuery object ready to go')

    # Use the cartesian product of all the list parameters to determine subqueries
    def get_query_list(self, params):
        # A couple params shouldn't get subqueried out:
        granule_list = params.pop('granule_list', None)
        product_list = params.pop('product_list', None)
        platform_list = params.pop('platform', None)

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
        final_list = []
        for q in query_list:
            if granule_list:
                q = q + tuple([{input_map()['granule_list'][0]: input_map()['granule_list'][1].format('{0}'.format(t))} for t in granule_list])
            if product_list:
                q = q + tuple([{input_map()['product_list'][0]: input_map()['product_list'][1].format('{0}'.format(t))} for t in product_list])
            if platform_list:
                q = q + tuple([{input_map()['platform'][0]: input_map()['platform'][1].format('{0}'.format(t))} for t in platform_list])
            final_list.append(q)
        return final_list

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
                if time.time() > self.cutoff_time:
                    logging.warning('Query ran too long, terminating')
                    logging.warning(self.params)
                    return
                if r is not None:
                    if self.max_results is None or self.result_counter < self.max_results:
                        self.result_counter += 1
                        yield r
                    else:
                        logging.debug('Max results reached, terminating')
                        return
            logging.debug('End of available results reached')
