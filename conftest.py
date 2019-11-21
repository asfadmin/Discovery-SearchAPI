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
        help = "Override which api ALL .yml tests use with this. (DEV/PROD or SOME-URL).")
    parser.addoption("--only-run", action="store", default=None,
        help = "Only run tests that contains this param in their name.")
    parser.addoption("--dont-run", action="store", default=None,
        help = "Dont run tests that contains this param in their name.")
    parser.addoption("--only-run-file", action="store", default=None,
        help = "Only run files that contain this in their name.")
    parser.addoption("--dont-run-file", action="store", default=None,
        help = "Dont run files that contain this in their name.")

@pytest.fixture
def cli_args(request):
    all_args = {}
    all_args['api'] = request.config.getoption('--api')
    all_args['only run'] = request.config.getoption('--only-run')
    all_args['dont run'] = request.config.getoption('--dont-run')
    all_args['only run file'] = request.config.getoption('--only-run-file')
    all_args['dont run file'] = request.config.getoption('--dont-run-file')
    return all_args

def loadTestsFromDirectory(dir_path, recurse=False):
    ####################
    # HELPER FUNCTIONS #
    ####################
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
    # Gets called for each yml/yaml file:
    def openFile(path):
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
                return None
        return yaml_dict
    # printTitleError: prints if moveTitleIntoTest cannot find the title:
    def printTitleError(test, file):
        print("\n###########")
        print("Yaml test '{0}' not formatted correctly: {1}.".format(str(test), file))
        print("###########\n")
    ##############
    # OPEN FILES #
    ##############
    list_of_tests = []
    for file in glob.glob(dir_path, recursive=recurse):
        yaml_dict = openFile(file)
        if yaml_dict == None:
            continue
        ##########################
        # ADDING "TYPE" TAG HERE #
        ##########################
        if "tests" in yaml_dict and isinstance(yaml_dict["tests"], type([])):
            for i, test in enumerate(yaml_dict["tests"]):
                test = moveTitleIntoTest(test)
                if test == None:
                    printTitleError(test, file)
                    continue
                if "test wkt" in test:
                    test["type"] = "WKT"
                elif "parser" in test and "input" in test:
                    test["type"] = "INPUT"
                else:
                    print("\nUnknownTest: {0}\n".format(test))
                yaml_dict["tests"][i] = test
            tests = yaml_dict["tests"]
        elif "url tests" in yaml_dict and isinstance(yaml_dict["url tests"], type([])):
            for i, test in enumerate(yaml_dict["url tests"]):
                test = moveTitleIntoTest(test)
                if test == None:
                    printTitleError("url tests", file)
                    continue
                test["type"] = "URL"
                yaml_dict["url tests"][i] = test
            tests = yaml_dict["url tests"]
        else:
            print("\n###########")
            print("No tests found in Yaml: {0}. Needs 'tests' key with a list as the value, or JUST a yml list.".format(dir_path))
            print("###########\n")
        #############################
        # READING FILE CONFIGS HERE #
        #############################
        # Store the configs for each file:
        file_config = {}
        file_config['yml name'] = os.path.basename(file)
        file_config['api'] = yaml_dict["api"] if "api" in yaml_dict else None
        file_config['print'] = yaml_dict["print"] if "print" in yaml_dict else None
        tests = zip(tests, itertools.repeat(file_config))
        list_of_tests.extend(tests)
    return list_of_tests

def setupTestFromConfig(test_info, file_config, cli_args):
    def getAPI(str_api, default="DEV"):
        # Stop 'http://str_api/params' from becoming 'http://str_api//params'
        if str_api == None:
            str_api = default

        # Check if a keyword:
        if str_api.upper() == "PROD":
            return "https://api.daac.asf.alaska.edu/"
        elif str_api.upper() == "TEST":
            return "https://api-test.asf.alaska.edu/"
        elif str_api.upper() == "DEV":
            return "http://127.0.0.1:5000/"
        # Else assume it IS a url:
        else:
            return str_api
    # Figure out which api to use:
    api_url = cli_args['api'] if cli_args['api'] != None else file_config['api']
    test_info['api'] = getAPI(api_url)

    return test_info

def skipTestsIfNecessary(test_info, file_config, cli_args):
    only_run_cli = cli_args['only run']
    dont_run_cli = cli_args['dont run']
    only_run_file_cli = cli_args['only run file']
    dont_run_file_cli = cli_args['dont run file']

    # If they passed '--only-run val', and val not in test title:
    if only_run_cli != None and only_run_cli.lower() not in test_info["title"].lower():
        pytest.skip("Title of test did not contain --only-run param (case insensitive)")
    # Same, but reversed for '--dont-run':
    if dont_run_cli != None and dont_run_cli.lower() in test_info["title"].lower():
        pytest.skip("Title of test contained --dont-run param (case insensitive)")
    # Same, but now for the file variants:
    if only_run_file_cli != None and only_run_file_cli.lower() not in file_config["yml name"].lower():
        pytest.skip("File test was in did not match --only-run-file param (case insensitive)")
    if dont_run_file_cli != None and dont_run_file_cli.lower() in file_config["yml name"].lower():
        pytest.skip("File test was in matched --dont-run-file param (case insensitive)")
