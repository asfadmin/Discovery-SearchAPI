import requests # for make_request
import json             # files stuff


# Incase I need to change endpoint interaction, I can do it all here:
def make_request(full_url, files=None, data=None):
    if data is None:
        data = {}
    try:
        r = requests.post(full_url, files=files, json=data)
    except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects) as e:
        assert False, "Cannot connect to API: {0}. Error: '{1}'.".format(full_url, str(e))
    return r

# Server returns 'json' as string. (Unless it's a server-error page).
# Last two params are just for helpfull error messages:
def request_to_json(request_str, url, test_title):
    try:
        request_json = json.loads(request_str)
    except (json.JSONDecodeError, json.decoder.JSONDecodeError) as e:
        assert False, "API did not return a json. (Error page?). URL: '{0}'. Title: '{1}'. Error: '{2}'. \nContent:\n{3}\n".format(url, test_title, str(e), str(request_str))
    return request_json


