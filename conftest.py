import pytest
import glob
import yaml
import os
import itertools


#####################
## BEGIN CLI STUFF ##
#####################

def pytest_addoption(parser):
    parser.addoption("--api", action="store", default=None,
        help = "Override which api ALL .yml tests use with this. (DEV/PROD or SOME-URL)")
    parser.addoption("--only-run", action="store", default=None,
        help = "Only run tests whos name begin with this parameter")

@pytest.fixture
def api_cli(request):
    return request.config.getoption('--api')

@pytest.fixture
def only_run_cli(request):
    return request.config.getoption('--only-run')

############################
## BEGIN HELPER FUNCTIONS ##
############################

def getAPI(str_api, params="", default="DEV"):
    # Stop 'http://str_api/params' from becoming 'http://str_api//params'
    if params[0:1] == '/':
        params = params[1:]
    if str_api == None:
        str_api = default

    # Check if a keyword:
    if str_api.upper() == "PROD":
        return "https://api.daac.asf.alaska.edu/" + params
    elif str_api.upper() == "TEST":
        return "https://api-test.asf.alaska.edu/" + params
    elif str_api.upper() == "DEV":
        return "http://127.0.0.1:5000/" + params
    # Else assume it IS a url:
    else:
        return str_api + params

def loadTestsFromDirectory(dir_path, recurse=False):
    list_of_tests = []
    print(dir_path)
    for file in glob.glob(dir_path, recursive=recurse):
        if not os.path.exists(file):
            print("\n###########")
            print("File not Found: {0}. Error: {1}".format(dir_path,str(e)))
            print("###########\n")
        with open(file, "r") as yaml_file:
            try:
                yaml_dict = yaml.safe_load(yaml_file)
            except yaml.YAMLError as e:
                print("\n###########")
                print("Failed to parse yaml: {0}. Error: {1}".format(dir_path,str(e)))
                print("###########\n")
                continue
            # Check 'if' it's the list of tests, vs it contains the list:
            if isinstance(yaml_dict, type([])):
                tests = yaml_dict
            elif "tests" in yaml_dict and isinstance(yaml_dict["tests"], type([])):
                tests = yaml_dict["tests"]
            else:
                print("\n###########")
                print("No tests found in Yaml: {0}. Needs 'tests' key with a list as the value, or JUST a yml list.".format(dir_path))
                print("###########\n")
                continue
            # Store the configs for each file:
            api = yaml_dict["API"] if "API" in yaml_dict else None
            tests = zip(tests, itertools.repeat(api))
            list_of_tests.extend(tests)
    return list_of_tests

# change from {"title_a" : {data1: 1,data2: 2}} to {title: "title_a", data1: 1, data2: 2},
#       or 'None' if impossible
def moveTitleIntoTest(json_test):
    keys = list(json_test.keys())
    if len(keys) != 1:
        return None
    title = keys[0]
    json_test = next(iter(json_test.values()))
    json_test["title"] = title
    return json_test