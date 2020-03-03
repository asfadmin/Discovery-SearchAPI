import requests
import json
from datetime import datetime

class test_date_parser():
    def __init__(self, test_info, file_conf, cli_args, test_vars):
        if cli_args["api"] != None:
            test_api = cli_args["api"]
        elif "api" in file_conf:
            test_api = file_conf["api"]
        else:
            assert False, "Endpoint test ran, but '--api' not declared in CLI (test_files_to_wkt).\nCan also add 'default' api to use in yml_tests/pytest_config.yml.\n"

        url_parts = [test_api, test_vars["endpoint"]]
        self.full_url = '/'.join(s.strip('/') for s in url_parts) # If both/neither have '/' between them, this still joins them correctly
        if "date" in test_info:
            self.full_url += "?date=" + test_info["date"]
        self.test_info = test_info

        response_json = self.makeRequest()

        self.runAssertTests(response_json)

    def makeRequest(self):
        r = requests.get(self.full_url)
        content = r.content.decode("utf-8")
        content_type = h.headers.get('content-type').split("/")[1]

        if content_type == "json":
            file_conf = json.loads(file_conf)
            if "error" in file_conf:
                content_type = "error json"
            elif "parsed" in file_conf:
                content_type = jsonlite
                file_conf

        return r.status_code, content_type, file_conf

    def runAssertTests(self, response_json):
        if "expected error" in test_info:
            if "error" in file_conf:
                assert test_info["expected error"].lower() in str(file_conf).lower(), "API returned a different error than expected. Test: '{0}'.".format(test_info["title"])
            else:
                assert False, "API parsed value when validation error expected. Test: '{0}'.".format(test_info["title"])
        if "expected date" in test_info:
            if "date" in file_conf:
                try:
                    time = datetime.strptime(file_conf["date"]["parsed"], "%Y-%m-%dT%H:%M:%SZ")
                except ValueError as e:
                    assert False, "API did not return the a date. Error Message: {1} Test: '{0}'.".format(test_info["title"], str(e))
            else:
                assert False, "API returned an unexpected parsing error. Test: '{0}'.".format(test_info["title"])

