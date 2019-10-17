import sys, os, pytest, yaml, ntpath, json
from geomet import wkt
import shapely.wkt


# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
resources_root = os.path.join(project_root, "unit_tests", "Resources")
sys.path.insert(0, project_root)
import APIUtils as test_file


class RunSingleShapeFromYaml():
    def __init__(self, json_dict):
        # Updates self.unit_tests w/ yaml:
        json_dict = self.applyDefaultValues(json_dict)

        # TODO: Add a test-checker here. (i.e. make sure expected wkt and 
        #       expected error aren't in same block)
        self.runRepairTest(json_dict)



    def applyDefaultValues(self, test_dict):
        # If you just say "expected wkt", switch that to the wrapped and unwrapped versions:
        if "expected wkt" in test_dict:
            wkt = test_dict["expected wkt"]
            del test_dict["expected wkt"]
            # Make expected wkt the default, if one of these are not declared:
            if "expected wkt wrapped" not in test_dict:
                test_dict["expected wkt wrapped"] = wkt
            if "expected wkt unwrapped" not in test_dict:
                test_dict["expected wkt unwrapped"] = wkt

        # Figure out what is expected to happen:
        pass_assertions = ["expected wkt wrapped", "expected wkt unwrapped", "repair"]
        fail_assertions = ["expected error msg"]
        # True if at least one of the above is used, False otherwise:
        test_dict["asserts pass"] = 0 != len([k for k,v in test_dict.items() if k in pass_assertions])
        test_dict["asserts fail"] = 0 != len([k for k,v in test_dict.items() if k in fail_assertions])

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
            if "expected wkt wrapped" in test_dict and "expected wkt unwrapped" in test_dict:
                # Shapely here because 30 != 30.000000 as strings
                assert shapely.wkt.loads(result["wkt"]["wrapped"]) == shapely.wkt.loads(test_dict["expected wkt wrapped"]), "WKT wrapped failed to match the result. Test: {0}".format(test_dict["title"])
                assert shapely.wkt.loads(result["wkt"]["unwrapped"]) == shapely.wkt.loads(test_dict["expected wkt unwrapped"]), "WKT unwrapped failed to match the result. Test: {0}".format(test_dict["title"])
            
            if test_dict["check repair"]:
                for repair in test_dict["repair"]:
                    assert repair in str(result["repairs"]), "Expected repair was not found in results. Test: {0}. Repairs done: {1}".format(test_dict["title"], result["repairs"])
                assert len(result["repairs"]) == len(test_dict["repair"]), "Number of repairs doesn't equal number of expected repairs. Test: {0}. Repairs done: {1}.".format(test_dict["title"],result["repairs"])
            
            if "expected error msg" in test_dict:
                assert test_dict["expected error msg"] in result["error"]["report"], "Got different error message than expected. Test: {0}.".format(test_dict["title"])



# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the parametrize:
yaml_name = os.path.splitext(os.path.basename(__file__))[0]+".yml"
yaml_path = os.path.join(project_root, "unit_tests", yaml_name)
if not os.path.exists(yaml_path):
    print("File not Found: " + yaml_path)
    exit(1)
with open(yaml_path, "r") as yaml_file:
    try:
        list_of_tests = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
        print("Failed to parse yaml: {0}".format(str(e)))
        exit(2)

@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachShapeInYaml(json_test):
    # change from {title: {data1: 1,data2: 2}} to {title: a, data1: 1, data2: 2}

    title = list(json_test.keys())[0]
    json_test = next(iter(json_test.values()))
    json_test["title"] = title
    RunSingleShapeFromYaml(json_test)
