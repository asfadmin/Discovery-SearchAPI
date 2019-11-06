import sys, os, yaml, json
import pytest, warnings
import geomet.wkt
import shapely.wkt
import requests
# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
resources_root = os.path.join(project_root, "unit_tests", "Resources")
sys.path.insert(0, project_root)
import APIUtils as test_file
import conftest as helpers



# url = "https://api.daac.asf.alaska.edu/services/utils/files_to_wkt"
# local_url = "http://127.0.0.1:5000/services/utils/files_to_wkt"
# files = {'files': open('unit_tests/Resources/shps_valid/PIGSearch.shp', 'rb')}
# r = requests.post(url, files=files)

# FilesToWKT(request).get_response()

# Add repair=False to make_response somehow, then:
# {'repair'='False', files': open('unit_tests/Resources/shps_valid/PIGSearch.shp', 'rb')}
#   assert "file_wkt" == wkt wrapped/unwrapped
#   assert repaired("file_wkt") == wkt repaired wrapped/unwrapped
#       (throw if they gave "")
def applyDefaultValues(test_dict):
    def applyIfNotExist(default, keys, test_dict):
        if not isinstance(keys, type([])):
            keys = [keys]
        for key in keys:
            if key not in test_dict:
                test_dict[key] = default
        return test_dict

    # Set 'repaired wkt' to the wrapped/unwrapped versions: 
    if "repaired wkt" in test_dict:
        default = test_dict["repaired wkt"]
        replace = ["repaired wkt wrapped", "repaired wkt unwrapped"]
        test_dict = applyIfNotExist(default, replace, test_dict)
        del test_dict["repaired wkt"]

    # Figure out what test is expected to do:
    pass_assertions = ["repaired wkt wrapped", "repaired wkt unwrapped", "repair", "parsed wkt"]
    fail_assertions = ["parsed error msg","repaired error msg"]
    # True if at least one of the above is used, False otherwise:
    test_dict["asserts pass"] = 0 != len([k for k,_ in test_dict.items() if k in pass_assertions])
    test_dict["asserts fail"] = 0 != len([k for k,_ in test_dict.items() if k in fail_assertions])
    # NOTE: possible for both to be true. If you load a file, check it's parse (pass assertion),
    #           then you check it's repair and expect it to error out.

    # Default Print the result to screen if tester isn't asserting anything:
    if "print" not in test_dict:
        if test_dict["asserts pass"] or test_dict["asserts fail"]:
            test_dict["print"] = False
        else:
            test_dict["print"] = True
    if "check repair" not in test_dict:
        repair_if_used = ["repaired wkt wrapped", "repaired wkt unwrapped", "repair"]
        if len([k for k,_ in test_dict.items() if k in repair_if_used]) > 0:
            test_dict["check repair"] = True
        else:
            test_dict["check repair"] = False

    # Add the repair if needed. Make sure it's a list:
    if "repair" not in test_dict:
        test_dict["repair"] = []
    elif not isinstance(test_dict["repair"], type([])):
        test_dict["repair"] = [test_dict["repair"]]

    # If you have nothing to test, skip it.
    if "test wkt" not in test_dict:
        pytest.skip("Test does not have 'test wkt:' param. Nothing to do.")
    # If they only passed one 'test wkt', turn it to a list:
    elif not isinstance(test_dict["test wkt"], type([])):
        test_dict["test wkt"] = [test_dict["test wkt"]]

    # Split the 'test wkt' into a list of files, and list of wkt's
    test_files = []
    test_wkts = []
    for test in test_dict["test wkt"]:
        # If file, move to test_files. If WKT, move to test_wkts:
        poss_path = os.path.join(resources_root, test)
        if os.path.isfile(poss_path):
            test_files.append(('files', open(poss_path, 'rb')))
        elif '/' in test:
            warnings.warn(UserWarning("File not found: {0}. File paths start after: '{1}'. (Test: {2})".format(poss_path, resources_root, test_info["title"])))
        else:
            test_wkts.append(test)
    # Split them to different keys:
    test_dict["test wkt"] = test_wkts
    test_dict["test file"] = test_files
    if len(test_dict["test file"]) == 0 and "parsed wkt" in test_dict:
        assert False, "Test: {0}. 'parsed wkt' declared, but no files were found to parse. Did you mean 'repaired wkt'?".format(test_info["title"])

    return test_dict

class ParseFileManager():
    def __init__(self, test_json):
        self.test = test_json
        url = test_json['api']
        wkt_files = test_json['test file']
        wkt_repair = { 'repair': False }
        try:
            r = requests.post(url, files=wkt_files, params=wkt_repair)
        except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects) as e:
            assert False, "Cannot connect to API: {0}.".format(url)

        self.status_code = r.status_code
        self.content = r.content.decode("utf-8").replace('"','')

    def run_assert_tests(self):
        assert self.status_code == 200, "API returned code: {0}".format(self.status_code)
        if "parsed error msg" in self.test:
            if "error" in self.content:
                assert self.test["parsed error msg"] in str(self.content)
            else:
                assert False, "API did not return the expected message. Test: {0}.".format(self.test["title"])
        if "parsed wkt" in self.test:
            if self.content[0] != "{":
                lhs = geomet.wkt.loads(self.content)
                rhs = geomet.wkt.loads(self.test["parsed wkt"])
                assert lhs == rhs, "Parsed wkt returned from API did not match 'parsed wkt'."
            else:
                assert False, "API did not return a WKT. Test: {0}".format(self.test["title"])

    def get_content(self):
        return self.content

class RepairWktManager():
    def __init__(self, test_json):
        num_shapes = len(test_json['test wkt'])
        if num_shapes == 0:
            return
        elif num_shapes == 1:
            test_shape = test_json['test wkt'][0]
        else:
            test_shape = "GEOMETRYCOLLECTION({0})".format(",".join(test_json['test wkt']))
        self.response = test_file.repairWKT(test_shape)
        self.test_json = test_json
    
    def run_assert_tests(self):
        if "repaired wkt wrapped" in self.test_json:
            if "wkt" in self.response:
                assert shapely.wkt.loads(self.response["wkt"]["wrapped"]) == shapely.wkt.loads(self.test_json["repaired wkt wrapped"]), "WKT wrapped failed to match the result. Test: {0}".format(self.test_json["title"])
            else:
                assert False, "WKT not found in response from API. Test: {0}. Response: {1}.".format(self.test_json["title"], self.response)
        if "repaired wkt unwrapped" in self.test_json:
            if "wkt" in self.response:
                assert shapely.wkt.loads(self.response["wkt"]["unwrapped"]) == shapely.wkt.loads(self.test_json["repaired wkt unwrapped"]), "WKT unwrapped failed to match the result. Test: {0}".format(self.test_json["title"])
            else:
                assert False, "WKT not found in response from API. Test: {0}. Response: {1}.".format(self.test_json["title"], self.response)

        if self.test_json["check repair"]:
            if "repairs" in self.response:
                for repair in self.test_json["repair"]:
                    assert repair in str(self.response["repairs"]), "Expected repair was not found in results. Test: {0}. Repairs done: {1}".format(self.test_json["title"], self.response["repairs"])
                assert len(self.response["repairs"]) == len(self.test_json["repair"]), "Number of repairs doesn't equal number of repaired repairs. Test: {0}. Repairs done: {1}.".format(self.test_json["title"],self.response["repairs"])
            else:
                assert False, "Unexpected WKT returned: {0}. Test: {1}".format(self.response, self.test_json["title"])
        if "repaired error msg" in self.test_json:
            if "error" in self.response:
                assert self.test_json["repaired error msg"] in self.response["error"]["report"], "Got different error message than expected. Test: {0}.".format(self.test_json["title"])
            else:
                assert False, "Unexpected WKT returned: {0}. Test: {1}".format(self.response, self.test_json["title"])
    def get_content(self):
        return self.response


# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the parametrize:
list_of_tests = []
yaml_path = os.path.join(project_root, "unit_tests", "test_APIUtils.yml")
list_of_tests.extend(helpers.loadTestsFromDirectory(yaml_path))
yaml_path = os.path.join(project_root, "unit_tests", "test_FilesToWKT.yml")
list_of_tests.extend(helpers.loadTestsFromDirectory(yaml_path))


@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachShapeInYaml(json_test, get_cli_args):
    # left = test itself, right = configs for ALL tests in that file
    test_info = json_test[0]
    file_config = json_test[1]

    # Load the cli arguments:
    api_cli = get_cli_args['api']
    only_run_cli = get_cli_args['only run']

    test_info = helpers.moveTitleIntoTest(test_info)
    if test_info == None:
        pytest.skip("Test does not have a title.")

    # If they passed '--only-run val', and val not in test title:
    if only_run_cli != None and only_run_cli not in test_info["title"]:
        pytest.skip("Title of test did not match --only-run param");

    # Apply default values to the test json:
    # i.e. Save 'repair wkt' to both the wrapped/unwrapped versions if needed
    test_info = applyDefaultValues(test_info)

    # Figure out which api to use:
    api_url = api_cli if api_cli != None else file_config['api']
    api_url = helpers.getAPI(api_url, params="/services/utils/files_to_wkt")
    test_info['api'] = api_url

    # Check if you need to print the start block:
    if test_info["print"]:
        print("\n#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        print(" > Test: " + test_info["title"])
        print("    api: " + str(test_info['api']))
        if len(test_info["test file"]) > 0:
            print("    Found {0} file(s) in test config.".format(len(test_info["test file"])))
        if len(test_info["test wkt"]) > 0:
            print("    Found {0} wkt(s) in test config.".format(len(test_info["test wkt"])))
        print()

    # RUN PARSED WKT TEST:
    if len(test_info["test file"]) > 0:
        parsed_info = ParseFileManager(test_info)
        if test_info["print"]:
            print("Parsed wkt before repair:")
            print(parsed_info.get_content())
            print()
        # Does nothing if you don't assert anything:
        parsed_info.run_assert_tests()
        # Errors are json, wkt's are strings:
        if parsed_info.get_content()[0] != '{':
            test_info["test wkt"].append(parsed_info.get_content())
 
    # RUN REPAIR WKT TEST:
    if len(test_info["test wkt"]) > 0:
        repair_info = RepairWktManager(test_info)
        if test_info["print"]:
            print("Repaired wkt json:")
            print(json.dumps(repair_info.get_content(), indent=4))

        repair_info.run_assert_tests()

