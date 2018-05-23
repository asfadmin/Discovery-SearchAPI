#!/bin/bash

# Shortcut for running tester.py with some default options on various maturities
if [ -z "$1" ]
then
    echo "Please specify a maturity."
    exit
fi
if [ $1 = "test" ]
then
    api="https://api-test.asf.alaska.edu/services/search/param"
elif [ $1 = "prod" ]
then
    api="https://api.daac.asf.alaska.edu/services/search/param"
else
    api="http://127.0.0.1:5000/services/search/param"
fi
echo "Testing maturity $1"
echo "API URL $api"
n="$(egrep '^\s*http' queries.txt | wc -l | egrep -o '\d+')"
echo "Running $n tests"
python tester.py -f queries.txt -s results.csv -c -r "$api"