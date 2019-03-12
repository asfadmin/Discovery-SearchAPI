import logging
from flask import Response, make_response, send_file
import api_headers
from threading import Thread
from uuid import uuid4 as uuid
from CMR.Output import output_translators, JSONLiteStreamArray
import json
import os

def run_threaded_caching_query(query, page_size):
    cache_id = uuid()
    logging.debug('cache_id: {0}'.format(cache_id))
    t = Thread(target=cache_results, args=(query, cache_id, page_size))
    logging.debug('Starting query thread')
    t.start()
    return cache_id

class CacheQuery:

    def __init__(self, query, cache_id, page_size):
        self.query = query
        self.cache_id = cache_id
        self.page_size = page_size
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
            if len(page) >= self.page_size:
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


def cache_results(query, cache_id, page_size):
    logging.debug('caching pages')
    cq = CacheQuery(query, cache_id, page_size)
    page_num = 0
    for page in cq.gen_pages():
        cq.save_page(page, page_num)
        page_num += 1

def response_from_cache(request):
    mimetype = output_translators()['jsonlite'][1]
    if 'cache_id' not in request.values or 'page' not in request.values:
        return Response(json.dumps({'error': 'Must provide cache ID (cache-id=) and page number (page=)'}, sort_keys=True, indent=4), 200, headers=api_headers.base(mimetype))
    cid = request.values['cache_id']
    p = request.values['page']
    cache_file_path = '{0}/jsonlite_cache/{1}/{2}.json'.format(os.getcwd(), cid, p)
    if not os.path.isfile(cache_file_path):
        return Response(json.dumps({'error': 'Requested cache file not found (cache_id={0}, page={1})'.format(cid, p)}, sort_keys=True, indent=4), 200, headers=api_headers.base(mimetype))
    response = make_response(send_file(cache_file_path))
    response.headers = api_headers.base(mimetype, response.headers)
    return response
