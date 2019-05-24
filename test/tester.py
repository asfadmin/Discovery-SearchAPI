#!/usr/bin/python

import argparse
import re
import subprocess
import os
import logging
import random

class tester:
    def __init__(self):

        parser = argparse.ArgumentParser(description='Read API query URLs from a file, test them, and gather statistics.')

        parser.add_argument('-f', '--file', action='store', required=True, help='File to read query URLs from')
        parser.add_argument('-s', '--save', action='store', required=True, help='CSV file to store results in')
        parser.add_argument('-c', '--cache', action='store_true', help='Save actual API results')
        parser.add_argument('-v', '--verbose', action='store_true', help='Verbose debugging output')
        parser.add_argument('-r', '--replace', action='store', help='Replace everything prior to the querystring')

        self.args = parser.parse_args()

        self.log = logging.getLogger('.{0}'.format(random.randint(0, 100)))

        if self.args.verbose is True:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

        base_fmt_str = "[%(process)s]: %(levelname)s: %(message)s (%(filename)s line %(lineno)d)"
        '''
        try:
            syslog_fmt = logging.Formatter(base_fmt_str)
            syslog = logging.handlers.SysLogHandler(address="/dev/log", facility=logging.handlers.SysLogHandler.LOG_LOCAL3)
            syslog.setFormatter(syslog_fmt)
            log.addHandler(syslog)
        except Exception as e:
            print("Issue with setting up /dev/log!!!")
        '''
        screen_and_file_fmt_str = "%(asctime)s.%(msecs)d " + base_fmt_str
        screen_and_file_fmt = logging.Formatter(screen_and_file_fmt_str, "%Y-%m-%dT%H:%M:%S")

        screenlog = logging.StreamHandler()
        screenlog.setFormatter(screen_and_file_fmt)
        self.log.addHandler(screenlog)

        self.log.debug("Logging setup with verbose = {0}".format(self.args.verbose))

        self.queries = None
        self.save_file = None

        if self.args.cache:
            try:
                os.mkdir('cache')
            except OSError:
                if not os.path.isdir('cache'):
                    raise

    def read_queries(self, f=None):
        if f is None:
            f = self.args.file
        self.log.debug('Reading query URLs from {0}'.format(f))
        try:
            with open(f, 'r') as query_file:
                self.queries = query_file.read().splitlines()
        except IOError as ioe:
            self.log.error(ioe)
            exit()
        return self.queries

    def run_queries(self):
        if self.args.save:
            self.save_file = open(self.args.save, 'w')
            self.save_file.write('params, http_status, total_time, download_speed, size_bytes, command\n')
        for q in self.queries:
            q = q.strip()
            if len(q) <= 0 or q[0] == '#':
                continue
            m = re.search(r'\?(.+)', q)
            p = m.group(1)
            if self.args.replace:
                q = '{0}?{1}'.format(self.args.replace, p)
            cache = ''
            if self.args.cache:
                try:
                    os.remove('cache/{0}'.format(p))
                except OSError:
                    pass
                cache = "-o 'cache/{0}'".format(p)
            else:
                cache = "-o /dev/null"
            c = "curl --silent --write-out '\"%{{http_code}}\",\"%{{time_total}}\",\"%{{speed_download}}\",\"%{{size_download}}\"' {0} '{1}'".format(cache, q)
            self.log.info('Executing {0}'.format(p))
            output = subprocess.check_output(c, shell=True)
            if self.args.save:
                self.save_file.write('"{0}", {1}, "{2}"\n'.format(p, output, c))
        if self.save_file:
            self.save_file.close()

# Entry point for running on command-line
if __name__ == '__main__':
    tester = tester()
    tester.read_queries()
    tester.run_queries()
