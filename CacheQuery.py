import logging
from threading import Thread
from asf_env import get_config
from uuid import uuid4 as uuid
from CMR.Output import output_translators, JSONLiteStreamArray
import itertools
import json
import os

def run_threaded_caching_query(query):
    cache_id = uuid()
    logging.debug('cache_id: {0}'.format(cache_id))
    t = Thread(target=cache_results, args=(query, cache_id))
    logging.debug('Starting query thread')
    t.start()
    return cache_id

class CacheQuery:

    def __init__(self, query, cache_id):
        self.query = query
        self.cache_id = cache_id
        self.results = []
        self.cache_path = '{0}/jsonlite_cache/{1}'.format(os.getcwd(), self.cache_id)
        try:
            os.makedirs(self.cache_path)
        except FileExistsError:
            pass


    def gen_pages(self):
        page = []
        for r in self.query.get_results():
            page.append(r)
            if len(page) >= 5:
                yield page
                page = []
        yield page

    def save_page(self, page, page_num):
        results = []
        for r in page:
            results.append(JSONLiteStreamArray.getItem(r))
        f_data = json.JSONEncoder(indent=2, sort_keys=True).encode({'results': results})
        with open('{0}/{1}.json'.format(self.cache_path, page_num), 'w') as cache_file:
            cache_file.write(f_data)
        return


def cache_results(query, cache_id):
    logging.debug('caching pages')
    cq = CacheQuery(query, cache_id)
    page_num = 0
    for page in cq.gen_pages():
        cq.save_page(page, page_num)
        page_num += 1
