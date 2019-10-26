import sys, os, yaml, json
import pytest, warnings
# from geomet import wkt
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

def sendFilesToWKTResponse(url, repair_files, repair_params={}):
    r = requests.post(url, files=repair_files, params=repair_params) # 'repair': 'True'
    if r.status_code != 200:
        assert False, "API returned code {0}. Content: {1}".format(r.status_code, r.content)
    return r.content.decode("utf-8").replace(" ", "").replace('"','')

class RunSingleShapeFromYaml():
    def __init__(self, json_dict):
        # Updates self.unit_tests w/ yaml:
        json_dict = self.__applyDefaultValues(json_dict)
        if "test path" in json_dict:
            json_dict = self.loadFile(json_dict)

        # TODO: Add a test-checker here. (i.e. make sure repaired wkt and 
        #       repaired error aren't in same block)
        self.runRepairTest(json_dict)



    def __applyDefaultValues(self, test_dict):
        # keys can be a string, or list of strings to check if inside of dict
        def applyIfNotExist(default, keys, test_dict):
            if not isinstance(keys, type([])):
                keys = [keys]
            for key in keys:
                if key not in test_dict:
                    test_dict[key] = default
            return test_dict

        # If you just say "repaired wkt", switch that to the wrapped and unwrapped versions:
        if "repaired wkt" in test_dict:
            default = test_dict["repaired wkt"]
            replace = ["repaired wkt wrapped", "repaired wkt unwrapped"]
            test_dict = applyIfNotExist(default, replace, test_dict)
            del test_dict["repaired wkt"]


        # Figure out what is repaired to happen:
        pass_assertions = ["repaired wkt wrapped", "repaired wkt unwrapped", "repair"]
        fail_assertions = ["expected error msg"]
        # True if at least one of the above is used, False otherwise:
        test_dict["asserts pass"] = 0 != len([k for k,_ in test_dict.items() if k in pass_assertions])
        test_dict["asserts fail"] = 0 != len([k for k,_ in test_dict.items() if k in fail_assertions])

        # Default Print the result to screen if tester isn't asserting anything:
        if "print" not in test_dict:
            if test_dict["asserts pass"] or test_dict["asserts fail"]:
                test_dict["print"] = False
            else:
                test_dict["print"] = True
       
        # Default Check the repairs if you're already thinking it will pass:
        if "check repair" not in test_dict:
            if test_dict["asserts pass"]:
                test_dict["check repair"] = True
            else:
                test_dict["check repair"] = False

        # Add the repair if needed. Make sure it's a list:
        if "repair" not in test_dict:
            test_dict["repair"] = []
        elif not isinstance(test_dict["repair"], type([])):
            test_dict["repair"] = [test_dict["repair"]]
        # else test_dict["repair"] is already a list

        return test_dict

    def runRepairTest(self, test_dict):
        test_wkt = test_dict["test wkt"]
        result = test_file.repairWKT(test_wkt)

        # Check if you need to print the block:
        if test_dict["print"] == True:
            print("\n#-#-#-#-#-#")
            print(" > Test: " + test_dict["title"])
            print(json.dumps(result, indent=4))

        if test_dict["asserts pass"] or test_dict["asserts fail"]:
            if "repaired wkt wrapped" in test_dict and "repaired wkt unwrapped" in test_dict:
                # Shapely here because 30 != 30.000000 as strings
                assert shapely.wkt.loads(result["wkt"]["wrapped"]) == shapely.wkt.loads(test_dict["repaired wkt wrapped"]), "WKT wrapped failed to match the result. Test: {0}".format(test_dict["title"])
                assert shapely.wkt.loads(result["wkt"]["unwrapped"]) == shapely.wkt.loads(test_dict["repaired wkt unwrapped"]), "WKT unwrapped failed to match the result. Test: {0}".format(test_dict["title"])
            
            if test_dict["check repair"]:
                for repair in test_dict["repair"]:
                    assert repair in str(result["repairs"]), "Expected repair was not found in results. Test: {0}. Repairs done: {1}".format(test_dict["title"], result["repairs"])
                assert len(result["repairs"]) == len(test_dict["repair"]), "Number of repairs doesn't equal number of repaired repairs. Test: {0}. Repairs done: {1}.".format(test_dict["title"],result["repairs"])
            
            if "expected error msg" in test_dict:
                assert test_dict["expected error msg"] in result["error"]["report"], "Got different error message than repaired. Test: {0}.".format(test_dict["title"])



# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the parametrize:
yaml_name = os.path.splitext(os.path.basename(__file__))[0]+".yml"
yaml_path = os.path.join(project_root, "unit_tests", yaml_name)
list_of_tests = helpers.loadTestsFromDirectory(yaml_path)

@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachShapeInYaml(json_test, api_cli, only_run_cli):
    test_info = json_test[0]
    api_file = json_test[1]

    test_info = helpers.moveTitleIntoTest(test_info)
    if test_info == None:
        pytest.skip("Test does not have a title.")

    # If they passed '--only-run val', and val not in test title:
    if only_run_cli != None and only_run_cli not in test_info["title"]:
        pytest.skip("Title of test did not match --only-run param")

    # If you have nothing to test...
    if "test wkt" not in test_info:
        pytest.skip("Test does not have 'test wkt:' param. Nothing to do.")

    # Figure out which api to use:
    api_url = api_cli if api_cli != None else api_file
    api_url = helpers.getAPI(api_url, params="/services/utils/files_to_wkt")

    # If they only passed one 'test wkt', turn it to a list:
    if not isinstance(test_info["test wkt"], type([])):
        test_info["test wkt"] = [test_info["test wkt"]]

    test_files = []
    test_wkts = []
    for test in test_info["test wkt"]:
        # If file, move to test_files. If WKT, move to test_wkts:
        poss_path = os.path.join(resources_root, test)
        if os.path.isfile(poss_path):
            test_files.append(('files', open(poss_path, 'rb')))
        elif '/' in test:
            warnings.warn(UserWarning("File not found: {0}. File paths start after: '{1}'. (Test: {2})".format(poss_path, resources_root, test_info["title"])))
        else:
            test_wkts.append(test)
    # Split them to different keys:
    test_info["test wkt"] = test_wkts
    test_info["test file"] = test_files
    
    if len(test_info["test file"]) == 0 and "parsed wkt" in json_test:
        warnings.warn(UserWarning("'parsed wkt' declared in {0} test, but no files were found to parse.".format(test_info["title"])))
    # if len(test_info["test file"]) > 0:

    # APPLY DEFAULT PARAMS HERE <--
    # THEN DO TEST FILE TESTS
    # THEN DO TEST WKT TESTS
    return







    if len(test_files) > 0:
        url = "http://127.0.0.1:5000/services/utils/files_to_wkt"
        if "parsed wkt" in json_test:
            parsed_wkt = sendFilesToWKTResponse(url, test_files, repair_params={'repair': 'False'})
            assert parsed_wkt == json_test["parsed wkt"].replace(" ", ""), "Parsed WKT did not match what was returned. API {0}".format(url)
        else:
            parsed_wkt = sendFilesToWKTResponse(url, test_files)
        test_wkts.append(parsed_wkt)

        # if "parsed wkt" in 
        # test_wkts.append()
    if len(test_wkts) == 1:
        json_test["test wkt"] = test_wkts[0]
    elif len(tests_wkt) > 1:
        json_test["test wkt"] = "GEOMETRYCOLLECTION("+",".join(test_wkts)+")"
    RunSingleShapeFromYaml(json_test)
