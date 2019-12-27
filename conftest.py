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

def loadTestsFromDirectory(dir_path_root, recurse=False):
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

    # Gets called for each yml/yaml file. Opens it and returns a dict:
    def openFile(path):
        if not os.path.exists(path):
            print("\n###########")
            print("File not Found: {0}. Error: {1}".format(path, str(e)))
            print("###########\n")
        with open(path, "r") as yaml_file:
            try:
                yaml_dict = yaml.safe_load(yaml_file)
            except yaml.YAMLError as e:
                print("\n###########")
                print("Failed to parse yaml: {0}. Error: {1}".format(path, str(e)))
                print("###########\n")
                return None
        return yaml_dict

    # printTitleError: prints if moveTitleIntoTest cannot find the title:
    def printTitleError(test, file):
        print("\n###########")
        print("Yaml test '{0}' not formatted correctly: {1}.".format(str(test), file))
        print("###########\n")


    ############################
    # SETUP TESTS / OPEN FILES #
    ############################
    tests = {}
    tests["BULK_DOWNLOAD"] = []
    tests["INPUT"] = []
    tests["URL"] = []
    tests["WKT"] = []
    tests_pattern = os.path.join(dir_path_root, "**", "test_*.y*ml")

    for file in glob.glob(tests_pattern, recursive=recurse):
        yaml_dict = openFile(file)
        if yaml_dict == None:
            continue

        # Store the configs from each file:
        file_config = {}
        file_config['api'] = yaml_dict["api"] if "api" in yaml_dict else None
        file_config['yml name'] = os.path.basename(file)
        file_config['print'] = yaml_dict["print"] if "print" in yaml_dict else None

        # Can't just do 'if elif' chain. I want to support if *both* 'tests' and 'url tests' are in the same file at once:
        hit_known_type = False
        if "tests" in yaml_dict and isinstance(yaml_dict["tests"], type([])):
            hit_known_type = True

            for test in yaml_dict["tests"]:
                test = moveTitleIntoTest(test)
                if test == None:
                    printTitleError(test, file)
                    continue

                test_with_config = (test, file_config)
                if "test wkt" in test:
                    tests["WKT"].append(test_with_config)
                elif "parser" in test and "input" in test:
                    tests["INPUT"].append(test_with_config)
                elif "account" in test:
                    tests["BULK_DOWNLOAD"].append(test_with_config)
                else:
                    print()
                    print("\nUNKNOWN TEST!! Title: '{0}'. File: '{1}'.\n".format(test["title"], file))
                    continue
                

        if "url tests" in yaml_dict and isinstance(yaml_dict["url tests"], type([])):
            hit_known_type = True
            for test in yaml_dict["url tests"]:
                test = moveTitleIntoTest(test)
                if test == None:
                    printTitleError("url tests", file)
                    continue
                tests["URL"].append((test, file_config))

        if not hit_known_type:
            print("\n###########")
            print("No tests found in Yaml: {0}. File needs 'tests' or 'url tests' key, with a list as the value.".format(dir_path_root))
            print("###########\n")
        #############################
        # READING FILE CONFIGS HERE #
        #############################
        # Key=Type of test, Val=List of tests. Add info from the file itself to 
        #      each individual test:
        # for _,val in tests.items():
        #     for i in range(len(val)):
        #         val[i-1] = (val, file_config)
    return tests

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
    if file_config["print"] != None:
        test_info["print"] = file_config["print"]
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
