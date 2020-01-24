#!/usr/bin/python

import argparse
import re
import requests
import multiprocessing
import random
import time

class bulk_query:
    def __init__(self, file, save, parallel, quiet):
        self.file = file
        self.save = save
        self.parallel = parallel
        self.quiet = quiet
        self.queries = None

    def read_queries(self):
        try:
            with open(self.file, 'r') as query_file:
                self.queries = []
                for q in query_file.read().splitlines():
                    q = q.strip()
                    if len(q) <= 0 or q[0] == '#':
                        continue
                    p = re.compile(r'\&?output\=\w+', re.IGNORECASE)
                    q = p.sub('', q)
                    q = q + '&output=jsonlite'
                    self.queries.append(q)
        except IOError as ioe:
            print(ioe)
            exit()
        random.shuffle(self.queries)
        return

    def run_query(self, q, s=None):
        if s is None:
            s = requests.Session()
        start = time.perf_counter()
        r = s.get(q)
        end = time.perf_counter()
        result = ''
        if r.status_code != 200:
            result = '"{0}","{1}","ERROR: HTTP status {2}"'.format(q, end - start, r.status_code)
        else:
            result = '"{0}","{1}"'.format(q, end - start)
        output_lock.acquire()
        if not self.quiet:
            print(result)
        with open(self.save, 'a') as save_file:
            save_file.write('{0}\n'.format(result))
        output_lock.release()
        return result

    def run_queries(self):
        pool = multiprocessing.Pool(self.parallel)

        with open(self.save, 'w') as save_file:
            save_file.write('"API Query","Duration (s)"\n')
        self.done(*pool.map(self.run_query, self.queries))

    def done(self, *whateva):
        pass

if __name__ == '__main__':
    output_lock = multiprocessing.Lock()
    parser = argparse.ArgumentParser(description='Read API query URLs from a file, test them, and gather statistics.')
    parser.add_argument('-f', '--file', action='store', required=True, help='File to read query URLs from')
    parser.add_argument('-s', '--save', action='store', required=True, help='File to save results to')
    parser.add_argument('-p', '--parallel', action='store', type=int, required=True, help='Number of queries to run in parallel')
    parser.add_argument('-q', '--quiet', action='store_true', required=False, help='Suppress screen output (does not affect file output)')

    args = parser.parse_args()
    querier = bulk_query(file=args.file, save=args.save, parallel=args.parallel, quiet=args.quiet)
    querier.read_queries()
    querier.run_queries()
    querier.done()
