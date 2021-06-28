import itertools
import logging
import time

from asf_env import get_config

from CMR.Translate import input_map
from CMR.SubQuery import CMRSubQuery
from flask import request


class CMRQuery:
    def __init__(self, req_fields, params=None, max_results=None):
        cfg = get_config()

        self.max_results = max_results
        self.req_fields = req_fields
        self.page_size = cfg['cmr_page_size']
        self.params = params

        provider = request.args.get("cmr_provider")
        if provider == None:
            provider = 'ASF'

        self.extra_params = [
            {'provider': provider},  # always limit the results to a provider, default 'ASF'
            {'page_size': self.max_results if self.is_small_max_results() else self.page_size},  # page size to request from CMR
            {'options[temporal][and]': 'true'}, # Makes handling date ranges easier
            {'sort_key[]': '-end_date'}, # Sort CMR results, but this is partially defeated by the subquery system
            {'sort_key[]': 'granule_ur'}, # Secondary sort key, the order these keys are specified in matters! This is to make multiple granules with the same date sort consistently
            {'options[platform][ignore_case]': 'true'}
        ]

        if cfg['cmr_scroll']:
            self.extra_params.append({'scroll': 'true'}) # Just leave this off if false, for the sake of the CMR team looking at logs

        self.result_counter = 0

        time_in_seconds = 14.5 * 60
        current_time = time.time()
        self.cutoff_time = current_time + time_in_seconds

        self.sub_queries = [
            CMRSubQuery(
                self.req_fields,
                params=list(query),
                extra_params=self.extra_params
            )
            for query in subquery_list_from(self.params)
        ]

        logging.debug('New CMRQuery object ready to go')

    def is_small_max_results(self):
        return (
            self.max_results is not None and
            self.max_results < self.page_size
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

                # it's a little silly but run this check again here so we don't accidentally fetch an extra page
                if self.max_results_reached():
                    logging.debug('Max results reached, terminating')
                    return

            logging.debug('End of available results reached')

    def is_out_of_time(self):
        return time.time() > self.cutoff_time

    def max_results_reached(self):
        return (
            self.max_results is not None and
            self.result_counter >= self.max_results
        )


def subquery_list_from(params):
    """
    Use the cartesian product of all the list parameters to
    determine subqueries
    """
    logging.debug('Building subqueries using params:')
    logging.debug(params)

    subquery_params, list_params = {}, {}

    def chunk_list(source_list, n):
        return [source_list[i * n:(i + 1) * n] for i in range((len(source_list) + n - 1) // n)]

    chunk_lists = ['granule_list', 'product_list'] # these list parameters will be broken into chunks for subquerying
    for chunk_type in chunk_lists:
        if chunk_type in params:
            params[chunk_type] = chunk_list(list(set(params[chunk_type])), 500) # distinct and split

    list_param_names = ['platform'] # these parameters will dodge the subquery system

    for k, v in params.items():
        if k in list_param_names:
            list_params[k] = v
        else:
            subquery_params[k] = v

    sub_queries = cartesian_product(subquery_params)
    formatted_list_params = format_list_params(list_params)

    final_sub_queries = [
        query + formatted_list_params for query in sub_queries
    ]

    logging.debug(f'{len(final_sub_queries)} subqueries built')

    return final_sub_queries


def cartesian_product(params):
    formatted_params = format_query_params(params)

    return list(itertools.product(*formatted_params))


def format_list_params(list_params):
    formatted_params = sum(format_query_params(list_params), [])

    return tuple(formatted_params)


def format_query_params(params):
    listed_params = []

    for param_name, param_val in params.items():
        plist = translate_param(param_name, param_val)
        listed_params.append(plist)

    return listed_params


def translate_param(param_name, param_val):
    param_list = []

    cmr_input_map = input_map()

    param_input_map = cmr_input_map[param_name]
    cmr_param = param_input_map[0]
    cmr_format_str = param_input_map[1]

    if not isinstance(param_val, list):
        param_val = [param_val]

    for l in param_val:
        format_val = l

        if isinstance(l, list):
            format_val = ','.join([f'{t}' for t in l])

        param_list.append({
            cmr_param: cmr_format_str.format(format_val)
        })

    return param_list
