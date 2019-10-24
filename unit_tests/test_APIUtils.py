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
            print("-----")
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
if not os.path.exists(yaml_path):
    print("File not Found: " + yaml_path)
    exit(1)
with open(yaml_path, "r") as yaml_file:
    try:
        yaml_dict = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
        print("Failed to parse yaml: {0}".format(str(e)))
        exit(2)

# If the yml IS the list of tests
if isinstance(yaml_dict, type([])):
    list_of_tests = yaml_dict
# If they gave the list of tests:
elif "tests" in yaml_dict:
    if isinstance(yaml_dict["tests"], type([])):
        list_of_tests = yaml_dict["tests"]
    else:
        assert False, "Error loading tests: Found 'tests' keyword, but you must have a yaml list as it's value"
else:
    assert False, "Error loading tests: Couldn't find 'tests' keyword in {0}, and the file itself was not a list.".format(yaml_name)

@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachShapeInYaml(json_test):
    # change from {"title_a" : {data1: 1,data2: 2}} to {title: "title_a", data1: 1, data2: 2}
    title = list(json_test.keys())[0]
    json_test = next(iter(json_test.values()))
    json_test["title"] = title
    if json_test["title"] != "local url debug":
        pytest.skip("tmp skip")

    # If you have nothing to test...
    if "test wkt" not in json_test:
        pytest.skip("Test does not have 'test wkt:' param. Nothing to do.")

    if not isinstance(json_test["test wkt"], type([])):
        json_test["test wkt"] = [json_test["test wkt"]]
    test_files = []
    test_wkts = []
    for test in json_test["test wkt"]:
        path = os.path.join(resources_root, test)
        if os.path.isfile(path):
            test_files.append(('files', open(path, 'rb')))
        elif '/' in test:
            warnings.warn(UserWarning("File not found: {0}. File paths start after: '{1}'.".format(path, resources_root)))
        else:
            # Else it's a wkt:
            test_wkts.append(test)

    r = requests.post("http://127.0.0.1:5000/services/utils/files_to_wkt", files=test_files)
    print("#############")
    print(r.status_code)
    print(r.content)
    print(test_files)
    # RunSingleShapeFromYaml(json_test)
