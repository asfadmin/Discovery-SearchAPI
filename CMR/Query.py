from itertools import product
import logging
import time
from CMR.Translate import input_map
from CMR.SubQuery import CMRSubQuery

class CMRQuery:

    def __init__(self, params=None, max_results=None, output='metalink', analytics=True):
        self.extra_params = {
            'provider': 'ASF', # always limit the results to ASF as the provider
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

        time_in_seconds = 14.5 * 60
        current_time = time.time()

        self.cutoff_time = current_time + time_in_seconds

        if self.is_small_max_results():
            self.extra_params['page_size'] = self.max_results

        query_list = get_query_list(self.params)
        self.sub_queries = [
            CMRSubQuery(
                params=list(query),
                extra_params=self.extra_params,
                analytics=self.analytics
            )
            for query in query_list
        ]

        logging.debug('New CMRQuery object ready to go')

    def is_small_max_results(self):
        return (
            self.max_results is not None and
            self.max_results < self.extra_params['page_size']
        )

    def get_count(self):
        return sum([sq.get_count() for sq in self.sub_queries])

    def get_results(self):
        for query_num, subquery in enumerate(self.sub_queries):
            logging.debug('Running subquery {0}'.format(query_num+1))

            # taking a page at a time from each subquery,
            # yield one result at a time until we max out
            for result in subquery.get_results():
                if self.is_out_of_time():
                    logging.warning('Query ran too long, terminating')
                    logging.warning(self.params)
                    return

                if self.max_results_reached():
                    logging.debug('Max results reached, terminating')
                    return

                if result is None:
                    continue

                self.result_counter += 1
                yield result

            logging.debug('End of available results reached')

    def is_out_of_time(self):
        return time.time() > self.cutoff_time

    def max_results_reached(self):
        return (
            self.max_results is not None and
            self.result_counter >= self.max_results
        )


def get_query_list(params):
    """
    Use the cartesian product of all the list parameters to
    determine subqueries
    """
    logging.debug('Building subqueries using params:')
    logging.debug(params)

    non_subquery_params = ['granule_list', 'product_list', 'platform']
    params_to_subquery = {
        k: v for k, v in params.items() if k not in non_subquery_params
    }

    sub_queries = cartesian_product(params_to_subquery)

    list_params = format_list_params([
        ['granule_list', params.get('granule_list', None)],
        ['product_list', params.get('product_list', None)],
        ['platform', params.get('platform', None)]
    ])

    final_queries = [
        query + list_params for query in sub_queries
    ]

    logging.debug(f'{len(final_queries)} subqueries built')

    return final_queries


def cartesian_product(params):
    params_in_itertools_format = itertools_product_fromat(params)

    return list(product(*params_in_itertools_format))


def itertools_product_fromat(params):
    listed_params = []
    cmr_input_map = input_map()

    for param_name, request_param in params.items():
        plist = []

        cmr_param = cmr_input_map[param_name][0]
        cmr_format_str = cmr_input_map[param_name][1]

        if not isinstance(request_param, list):
            request_param = [request_param]

        for l in request_param:
            format_param_val = l

            if isinstance(l, list):
                format_param_val = (
                    ','.join([f'{t}' for t in l])
                )

            plist.append({
                cmr_param: cmr_format_str.format(format_param_val)
            })

        listed_params.append(plist)

    return listed_params


def format_list_params(list_params):
    cmr_input_map = input_map()
    cmr_param_format = tuple()

    for list_name, list_param in list_params:
        if not list_param:
            continue

        list_input_map = cmr_input_map[list_name]
        cmr_name, cmr_format_str = list_input_map[0], list_input_map[1]

        cmr_param_format += tuple([
            {cmr_name: cmr_format_str.format(f'{list_param_val}')}
            for list_param_val in list_param
        ])

    return cmr_param_format
