import requests
import json
from datetime import datetime

class test_date_parser():
    def __init__(self, **args):
        self.error_msg = "Reason: {0}"
        test_info = args["test_info"]
        test_api = args["config"].getoption("--api")["this_api"]


        url_parts = [test_api, args["test_type_vars"]["endpoint"]]
        self.full_url = '/'.join(s.strip('/') for s in url_parts) # If both/neither have '/' between them, this still joins them correctly
        if "date" in test_info:
            self.full_url += "?date=" + test_info["date"]
        self.error_msg += "\n - URL: '{0}'.".format(self.full_url)

        self.test_info = test_info

        (status_code, content_type, content) = self.makeRequest()
        self.applyDefaultValues()
        self.runAssertTests(status_code, content_type, content)

    def makeRequest(self):
        r = requests.get(self.full_url)
        h = requests.head(self.full_url)
        content = r.content.decode("utf-8")
        content_header = h.headers.get('content-type')
        try:
            content_type = content_header.split("/")[1]
        except AttributeError:
            assert False, self.error_msg.format("Header is not formatted as expected. Header: {0}.\nFile Content (First 500 char): \n{1}\n".format(content_header, content[:500]))


        if content_type == "json":
            try:
                content = json.loads(content)
            except json.decoder.JSONDecodeError:
                assert False, self.error_msg.format("API did not return a json, but content_type said it did.\nReturned content (First 500 char): \n{0}\n".format(content[:500]))
            if "errors" in content: 
                content_type = "error json"
        return r.status_code, content_type, content

    def applyDefaultValues(self):
        if "expected date" in self.test_info:
            if "expected file" not in self.test_info:
                self.test_info["expected file"] = "json"
            if "expected code" not in self.test_info:
                self.test_info["expected code"] = 200
        if "expected error" in self.test_info:
            if "expected file" not in self.test_info:
                self.test_info["expected file"] = "error json"
            if "expected code" not in self.test_info:
                self.test_info["expected code"] = 200

    def runAssertTests(self, status_code, content_type, content):
        if content_type == "html" or status_code >= 500:
            assert False, self.error_msg.format("API returned error page. \nHTML (First 500 char):\n{0}\n".format(content[:500]))
        if "expected error" in self.test_info:
            if "error" in content:
                assert self.test_info["expected error"].lower() in str(content).lower(), self.error_msg.format("API returned a different error than expected.")
            else:
                assert False, self.error_msg.format("API parsed value when validation error expected.")
        if "expected date" in self.test_info:
            if "date" in content:
                try:
                    datetime.strptime(content["date"]["parsed"], "%Y-%m-%dT%H:%M:%SZ")
                except (ValueError, TypeError) as e:
                    assert False, self.error_msg.format("API did not return a date. Error Message: '{0}'.\n - API Returned: {1}.\n".format(str(e), content))
            else:
                assert False, self.error_msg.format("API did not return a date. Returned (First 500 char):\n{0}\n".format(content[:500]))
        if "expected code" in self.test_info:
            assert self.test_info["expected code"] == status_code, self.error_msg.format("API returned different error code than expected. Code returned: {0}, Expected: {1}.".format(status_code, self.test_info["expected code"]))
