import requests
import json

class test_mission_list():
    def __init__(self, test_info, file_conf, cli_args, test_vars):
        if cli_args["api"] != None:
            test_api = cli_args["api"]
        elif "api" in file_conf:
            test_api = file_conf["api"]
        else:
            assert False, "Endpoint test ran, but '--api' not declared in CLI (test_files_to_wkt).\nCan also add 'default' api to use in yml_tests/pytest_config.yml.\n"

        url_parts = [test_api, test_vars["endpoint"]]
        self.full_url = '/'.join(s.strip('/') for s in url_parts) # If both/neither have '/' between them, this still joins them correctly
        if "platform" in test_info:
        	self.full_url += "?platform=" + test_info["platform"]
        self.test_info = test_info

        response_json = self.makeRequest()

        self.runAssertTests(response_json)

    def makeRequest(self):
    	r = requests.get(self.full_url)
    	assert r.status_code == 200, "API returned code: {0}. Test: {1}. URL: {2}.".format(r.status_code, self.test_info["title"], self.full_url)
    	content = r.content.decode("utf-8")
    	try:
    		json_content = json.loads(content)
    	except json.JSONDecodeError as e:
    		assert False, "API did not return JSON. Test: {0} URL: {1}.\nReturned:\n{2}\n".format(self.test_info["title"], self.full_url, content)
    	return json_content

    def runAssertTests(self, response_json):
    	assert "result" in response_json, "'result' key not found in JSON. Test: {0} URL: {1}.\nReturned:\n{2}\n".format(self.test_info["title"], self.full_url, response_json)
    	if "misson_list_size_min" in self.test_info:
    		assert int(self.test_info["misson_list_size_min"]) <= len(response_json["result"]), "Too few results returned. Test: {0} URL: {1}.".format(self.test_info["title"], self.full_url)
