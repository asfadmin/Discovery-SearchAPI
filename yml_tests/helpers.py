import pytest, warnings # for testing
import requests # for make_request
import json             # files stuff


# Incase I need to change endpoint interaction, I can do it all here:
def make_request(full_url, files=None, data={}):
    try:
        r = requests.post(full_url, files=files, data=data)
    except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects) as e:
        assert False, "Cannot connect to API: {0}.".format(full_url)
    return r

# Server returns 'json' as string. (Unless it's a server-error page).
# Last two params are just for helpfull error messages:
def request_to_json(request_str, url, test_title):
    try:
        request_json = json.loads(request_str)
    except (json.JSONDecodeError, json.decoder.JSONDecodeError) as e:
        assert False, "API did not return a json. (Error page?). URL: '{0}'. Title: '{1}'. \nContent:\n{2}\n".format(url, test_title, str(request_str))
    return request_json


