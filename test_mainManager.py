import os, sys, re
import pytest, warnings
import requests, urllib
import geomet, shapely
import json, csv, yaml
import pexpect

from copy import deepcopy
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conftest as helpers
import APIUtils as test_repair
import CMR.Input as test_input




###############
## WKT TESTS ##
###############
class WKT_Manager():
    def __init__(self, test_dict):
        test_dict = self.applyDefaultValues(test_dict)
        # TESTING FILES:
        if len(test_dict["test file"]) > 0:
            FileLoader = self.ParseFileManager(test_dict)
            poss_wkt = FileLoader.getContent()

            if test_dict["print"] == True:
                print("\nParsed wkt before repair:")
                print(poss_wkt)
                print()

            # Does nothing if you don't assert anything:
            FileLoader.runAssertTests()
            # Errors are json strings, wkt's are plain strings:
            if isinstance(poss_wkt, str) and poss_wkt[ 0] != '{':
                test_dict["test wkt"].append(poss_wkt)

        # TESTING WKTS:
        if len(test_dict["test wkt"]) > 0:
            WktLoader = self.RepairWKTManager(test_dict)
            poss_wkt = WktLoader.getContent()

            if test_dict['print'] == True:
                print("\nWkt after repair:")
                print(poss_wkt)
                print()

            # Does nothing if you don't assert anything:
            WktLoader.runAssertTests()


    def applyDefaultValues(self, test_dict):
        # Copy 'repaired wkt' to the wrapped/unwrapped versions if used:
        if "repaired wkt" in test_dict:
            for i in ["repaired wkt wrapped", "repaired wkt unwrapped"]:
                if i not in test_dict:
                    test_dict[i] = test_dict["repaired wkt"]
            del test_dict["repaired wkt"]
    
        # Figure out what test is 'expected' to do:
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
        
        # If they only passed one 'test wkt', turn it to a list:
        if not isinstance(test_dict["test wkt"], type([])):
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
                warnings.warn(UserWarning("File not found: {0}. File paths start after: '{1}'. (Test: {2})".format(poss_path, resources_root, test_dict["title"])))
            else:
                test_wkts.append(test)
        # If you expect to test a file parse, but no files were given:
        if len(test_files) == 0 and "parsed wkt" in test_dict:
            assert False, "Test: {0}. 'parsed wkt' declared, but no files were found to parse. Did you mean 'repaired wkt'?".format(test_info["title"])
        # Split them to different keys, (BOTH are lists at this point too):
        test_dict["test wkt"] = test_wkts
        test_dict["test file"] = test_files
        return test_dict

    class ParseFileManager():
        def __init__(self, test_dict):
            url = test_dict['api']
            wkt_files = test_dict['test file']
            wkt_repair = { 'repair': False }
            try:
                r = requests.post(url, files=wkt_files, params=wkt_repair)
            except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects) as e:
                assert False, "Cannot connect to API: {0}.".format(url)

            self.status_code = r.status_code
            self.content = r.content.decode("utf-8").replace('"','')
            self.test_dict = test_dict

        def getContent(self):
            return self.content

        def runAssertTests(self):
            assert self.status_code == 200, "API returned code: {0}".format(self.status_code)
            if "parsed error msg" in self.test_dict:
                if "error" in self.content:
                    assert self.test_dict["parsed error msg"] in str(self.content)
                else:
                    assert False, "API did not return the expected message. Test: {0}.".format(self.test_dict["title"])
            if "parsed wkt" in self.test_dict:
                if self.content[0] != "{":
                    lhs = geomet.wkt.loads(self.content)
                    rhs = geomet.wkt.loads(self.test_dict["parsed wkt"])
                    assert lhs == rhs, "Parsed wkt returned from API did not match 'parsed wkt'."
                else:
                    assert False, "API did not return a WKT. Test: {0}".format(self.test_dict["title"])

    class RepairWKTManager():
        def __init__(self, test_dict):
            num_shapes = len(test_dict['test wkt'])
            if num_shapes == 0:
                return
            elif num_shapes == 1:
                test_shape = test_dict['test wkt'][0]
            else:
                test_shape = "GEOMETRYCOLLECTION({0})".format(",".join(test_dict['test wkt']))
            self.content = test_repair.repairWKT(test_shape)
            self.test_dict = test_dict

        def getContent(self):
            return self.content

        def runAssertTests(self):
            if "repaired wkt wrapped" in self.test_dict:
                if "wkt" in self.content:
                    assert shapely.wkt.loads(self.content["wkt"]["wrapped"]) == shapely.wkt.loads(self.test_dict["repaired wkt wrapped"]), "WKT wrapped failed to match the result. Test: {0}".format(self.test_dict["title"])
                else:
                    assert False, "WKT not found in response from API. Test: {0}. Response: {1}.".format(self.test_dict["title"], self.content)
            if "repaired wkt unwrapped" in self.test_dict:
                if "wkt" in self.content:
                    assert shapely.wkt.loads(self.content["wkt"]["unwrapped"]) == shapely.wkt.loads(self.test_dict["repaired wkt unwrapped"]), "WKT unwrapped failed to match the result. Test: {0}".format(self.test_dict["title"])
                else:
                    assert False, "WKT not found in response from API. Test: {0}. Response: {1}.".format(self.test_dict["title"], self.content)

            if self.test_dict["check repair"]:
                if "repairs" in self.content:
                    for repair in self.test_dict["repair"]:
                        assert repair in str(self.content["repairs"]), "Expected repair was not found in results. Test: {0}. Repairs done: {1}".format(self.test_dict["title"], self.content["repairs"])
                    assert len(self.content["repairs"]) == len(self.test_dict["repair"]), "Number of repairs doesn't equal number of repaired repairs. Test: {0}. Repairs done: {1}.".format(self.test_dict["title"],self.content["repairs"])
                else:
                    assert False, "Unexpected WKT returned: {0}. Test: {1}".format(self.content, self.test_dict["title"])
            if "repaired error msg" in self.test_dict:
                if "error" in self.content:
                    assert self.test_dict["repaired error msg"] in self.content["error"]["report"], "Got different error message than expected. Test: {0}.".format(self.test_dict["title"])
                else:
                    assert False, "Unexpected WKT returned: {0}. Test: {1}".format(self.content, self.test_dict["title"])


#################
## INPUT TESTS ##
#################
class INPUT_Manager():
    def __init__(self, test_dict):
        # Create map/dict for which parser to use:
        # Note: Only parsers that accept exactly one val are here
        parsers = {}
        parsers["parse_string"] = test_input.parse_string
        parsers["parse_int"] = test_input.parse_int
        parsers["parse_float"] = test_input.parse_float
        parsers["parse_date"] = test_input.parse_date

        parsers["parse_date_range"] = test_input.parse_date_range
        parsers["parse_int_range"] = test_input.parse_int_range
        parsers["parse_float_range"] = test_input.parse_float_range

        parsers["parse_string_list"] = test_input.parse_string_list
        parsers["parse_int_list"] = test_input.parse_int_list
        parsers["parse_float_list"] = test_input.parse_float_list

        parsers["parse_int_or_range_list"] = test_input.parse_int_or_range_list
        parsers["parse_float_or_range_list"] = test_input.parse_float_or_range_list

        parsers["parse_coord_string"] = test_input.parse_coord_string
        parsers["parse_bbox_string"] = test_input.parse_bbox_string
        parsers["parse_point_string"] = test_input.parse_point_string
        parsers["parse_wkt"] = test_input.parse_wkt

        self.parsers = parsers
        self.test_dict = test_dict
        self.should_print = ("expected" not in test_dict and "expected error" not in test_dict) \
                        or ("print" in test_dict and test_dict["print"] == True)
        if self.should_print:
            print("\nInput CMR Test:")

        if "parser" in test_dict and "input" in test_dict:
            self.runAssertTests()


    def runAssertTests(self):
        parser = self.test_dict["parser"]
        test_input = self.test_dict["input"]
        try:
            val = self.parsers[parser](test_input)
        except Exception as e:
            val = str(e)

        if self.should_print:
            print(val)
            print()

        if "expected" in self.test_dict:
            assert self.test_dict["expected"] == val, "CMR INPUT: expected doesn't match output. Test: {0}.".format(self.test_dict["title"])
        if "expected error" in self.test_dict:
            assert self.test_dict["expected error"] in val, "CMR INPUT: expected error doesn't match output error. Test: {0}.".format(self.test_dict["title"])


###############
## URL TESTS ##
###############
class URL_Manager():
    def __init__(self, test_dict):
        # Get the url string and if assert was used:
        self.query, assert_used = self.getUrl(test_dict)
        status_code, content_type, file_content = self.runQuery()


        # Figure out if you should print stuff:
        if "print" not in test_dict:
            test_dict["print"] = False if assert_used else True

        if assert_used:
            self.runAssertTests(test_dict, status_code, content_type, file_content)

    def runAssertTests(self, test_dict, status_code, content_type, file_content):
        if "expected code" in test_dict:
            assert test_dict["expected code"] == status_code, "Status codes is different than expected. Test: {0}. URL: {1}.".format(test_dict["title"], self.query)
        if "expected file" in test_dict:
            assert test_dict["expected file"] == content_type, "Different file type returned than expected. Test: {0}. URL: {1}.".format(test_dict["title"], self.query)
            # If you expect it to be a ligit file, and 'file_content' was converted from str to dict:
            if content_type[0:5] not in ["error", "blank"] and isinstance(file_content, type({})):
                ### BEGIN TESTING FILE CONTENTS:
                test_dict = self.parseTestValues(test_dict)
                file_content = self.renameKeysToStandard(file_content)
                file_content = self.renameValsToStandard(file_content)
                # print(json.dumps(test_dict, indent=4, default=str))
                # IF used in url, IF contained in file's content, check if they match
                def checkFileContainsExpected(key, url_dict, file_dict):
                    # print(url_dict)
                    # print("CHECKING FILE HERE")
                    # print(file_dict)
                    # print(json.dumps(file_dict, indent=4, default=str))
                    if key in url_dict and key in file_dict:
                        found_in_list = False
                        for found_param in file_dict[key]:
                            # poss_list is either single "i", or range "[i,j]":
                            for poss_list in url_dict[key]:
                                # If it's a list, then it is a range of numbers:
                                if isinstance(poss_list, type([])):
                                    expect_type = type(poss_list[0])
                                    # "found_param" is always a string. Convert it to match
                                    if expect_type(found_param) >= poss_list[0] and expect_type(found_param) <= poss_list[1]:
                                        found_in_list = True
                                        break
                                # This part gets hit for single numbers, and strings. (ie "Platform"):
                                else:
                                    expect_type = type(poss_list)
                                    if expect_type(found_param) == poss_list:
                                        found_in_list = True
                                        break
                            # If inner for-loop found it, break out of this one too:
                            if found_in_list == True:
                                break
                        assert found_in_list, key + " declared, but not found in file. Test: {0}".format(test_dict["title"])
                
                def checkMinMax(key, url_dict, file_dict):
                    if "min"+key in url_dict and key in file_dict:
                        for value in file_dict[key]:
                            number_type = type(url_dict["min"+key])
                            assert number_type(value) >= url_dict["min"+key], "TESTING"
                    if "max"+key in url_dict and key in file_dict:
                        for value in file_dict[key]:
                            number_type = type(url_dict["max"+key])
                            assert number_type(value) <= url_dict["max"+key], "TESTING"


                checkFileContainsExpected("Platform", test_dict, file_content)
                checkFileContainsExpected("absoluteOrbit", test_dict, file_content)
                checkFileContainsExpected("asfframe", test_dict, file_content)
                checkFileContainsExpected("granule_list", test_dict, file_content)
                checkFileContainsExpected("groupid", test_dict, file_content)
                checkFileContainsExpected("flightdirection", test_dict, file_content)
                checkFileContainsExpected("offnadirangle", test_dict, file_content)
                checkFileContainsExpected("polarization", test_dict, file_content)
                checkFileContainsExpected("relativeorbit", test_dict, file_content)
                checkFileContainsExpected("collectionname", test_dict, file_content)
                checkFileContainsExpected("beammode", test_dict, file_content)

                checkMinMax("baselineperp", test_dict, file_content)
                checkMinMax("doppler", test_dict, file_content)
                checkMinMax("insarstacksize", test_dict, file_content)
                checkMinMax("faradayrotation", test_dict, file_content)
    def parseTestValues(self, test_dict):
        # Turn string values to lists:
        mutatable_dict = deepcopy(test_dict)
        try:
            # Dictionary changes sizes, so check one dict, and make  thechanges to other
            for key, val in test_dict.items():
                # The Input.parse* methods all expect a string:
                val = str(val)
                if key.lower() == "absoluteorbit":
                    del mutatable_dict[key]
                    mutatable_dict["absoluteOrbit"] = test_input.parse_int_or_range_list(val)
                elif key.lower() == "platform":
                    del mutatable_dict[key]
                    mutatable_dict["Platform"] = test_input.parse_string_list(val)
                elif key.lower() in ["frame", "asfframe"]:
                    del mutatable_dict[key]
                    mutatable_dict["asfframe"] = test_input.parse_int_or_range_list(val)
                elif key.lower() == "granule_list":
                    del mutatable_dict[key]
                    mutatable_dict["granule_list"] = test_input.parse_string_list(val)
                elif key.lower() == "groupid":
                    del mutatable_dict[key]
                    mutatable_dict["groupid"] = test_input.parse_string_list(val)
                elif key.lower() == "flightdirection":
                    del mutatable_dict[key]
                    mutatable_dict["flightdirection"] = test_input.parse_string_list(val)
                elif key.lower() == "offnadirangle":
                    del mutatable_dict[key]
                    mutatable_dict["offnadirangle"] = test_input.parse_float_or_range_list(val)
                elif key.lower() == "polarization":
                    del mutatable_dict[key]
                    val = urllib.parse.unquote_plus(val)
                    mutatable_dict["polarization"] = test_input.parse_string_list(val)
                elif key.lower() == "relativeorbit":
                    del mutatable_dict[key]
                    mutatable_dict["relativeorbit"] = test_input.parse_int_or_range_list(val)
                elif key.lower() == "collectionname":
                    del mutatable_dict[key]
                    val = urllib.parse.unquote_plus(val)
                    mutatable_dict["collectionname"] = test_input.parse_string_list(val)
                elif key.lower() in ["beammode", "beamswath"]:
                    del mutatable_dict[key]
                    mutatable_dict["beammode"] = test_input.parse_string_list(val)
                # MIN/MAX variants
                # min/max BaselinePerp
                elif key.lower()[3:] == "baselineperp":
                    del mutatable_dict[key]
                    # Save the min/max key, all lower
                    mutatable_dict[key.lower()[0:3]+"baselineperp"] = test_input.parse_float(val)
                # min/max Doppler:
                elif key.lower()[3:] == "doppler":
                    del mutatable_dict[key]
                    mutatable_dict[key.lower()[0:3]+"doppler"] = test_input.parse_float(val)
                # min/max InsarStackSize:
                elif key.lower()[3:] == "insarstacksize":
                    del mutatable_dict[key]
                    mutatable_dict[key.lower()[0:3]+"insarstacksize"] = test_input.parse_int(val)
                #min/max FaradayRotation:
                elif key.lower()[3:] == "faradayrotation":
                    del mutatable_dict[key]
                    mutatable_dict[key.lower()[0:3]+"faradayrotation"] = test_input.parse_float(val)

        except ValueError as e:
            assert False, "Test: {0}. Incorrect parameter: {1}".format(test_dict["title"], str(e))
        test_dict = mutatable_dict
        # Make each possible value line up with what the files returns:
        test_dict = self.renameValsToStandard(test_dict)
        return test_dict

    def renameKeysToStandard(self, json_dict):
        ### absoluteOrbit:
        if "Orbit" in json_dict:
            json_dict["absoluteOrbit"] = json_dict.pop("Orbit")
        ### asfframe:
        for key in ["frame", "frameNumber", "Frame Number"]:
            if key in json_dict:
                json_dict["asfframe"] = json_dict.pop(key)
        ### granule_list:
        for key in ["granuleName", "Granule Name"]:
            if key in json_dict:
                json_dict["granule_list"] = json_dict.pop(key)
        ### groupid:
        if "groupID" in json_dict:
            json_dict["groupid"] = json_dict.pop("groupID")
        ### flightDirection
        for key in ["Ascending or Descending?", "flightDirection"]:
            if key in json_dict:
                json_dict["flightdirection"] = json_dict.pop(key)
        ### offNadirAngle:
        for key in ["Off Nadir Angle", "offNadirAngle"]:
            if key in json_dict:
                json_dict["offnadirangle"] = json_dict.pop(key)
        ### polarization:
        if "polarization" in json_dict:
            json_dict["polarization"] = json_dict.pop("polarization")
        ### relativeOrbit:
        for key in ["relativeOrbit", "Path Number"]:
            if key in json_dict:
                json_dict["relativeorbit"] = json_dict.pop(key)
        ### collectionName:
        if "collectionName" in json_dict:
            json_dict["collectionname"] = json_dict.pop("collectionName")
        ### beamMode:
        for key in ["beamswath", "beamMode", "Beam Mode"]:
            if key in json_dict:
                json_dict["beammode"] = json_dict.pop(key)
        ### min/max BaselinePerp:
        for key in ["Baseline Perp.", "baselinePerp"]:
            if key in json_dict:
                json_dict["baselineperp"] = json_dict.pop(key)
        ### min/max Doppler:
        for key in ["doppler", "Doppler"]:
            if key in json_dict:
                json_dict["doppler"] = json_dict.pop(key)
        ### min/max InsarStackSize:
        for key in ["insarStackSize", "Stack Size"]:
            if key in json_dict:
                json_dict["insarstacksize"] = json_dict.pop(key)
        for key in ["faradayRotation", "Faraday Rotation"]:
            if key in json_dict:
                json_dict["faradayrotation"] = json_dict.pop(key)
        return json_dict


    # assumes values are in the form of {key: [value1,value2]}
    def renameValsToStandard(self, json_dict):
        if "Platform" in json_dict:
            itter_copy = deepcopy(json_dict)
            for i, platform in enumerate(itter_copy["Platform"]):
                if platform == None:
                    continue
                #####
                # NOTE: UPPER for when adding platforms in future:
                platform = platform.upper()
                # ALOS
                if platform in ["ALOS", "A3"]:
                    json_dict["Platform"][i] = "ALOS"
                # AIRSAR
                elif platform in ["AIRSAR", "AS"]:
                    json_dict["Platform"][i] = "AIRSAR"
                # ERS
                elif platform in ["ERS"]:
                    json_dict["Platform"][i] = "ERS"
                # ERS-1
                elif platform in ["ERS-1", "E1"]:
                    json_dict["Platform"][i] = "ERS-1"
                # ERS-2
                elif platform in ["ERS-2", "E2"]:
                    json_dict["Platform"][i] = "ERS-2"
                # JERS-1
                elif platform in ["JERS-1", "J1"]:
                    json_dict["Platform"][i] = "JERS-1"
                # RADARSAT-1
                elif platform in ["RADARSAT-1", "R1"]:
                    json_dict["Platform"][i] = "RADARSAT-1"
                # SEASAT
                elif platform in ["SEASAT", "SS"]:
                    json_dict["Platform"][i] = "SEASAT"
                # Sentinel-1:
                elif platform in ["S1", "SENTINEL-1", "SENTINEL"]:
                    del json_dict["Platform"][i]
                    json_dict["Platform"].append("Sentinel-1A")
                    json_dict["Platform"].append("Sentinel-1B")
                # Sentinel-1A
                elif platform in ["SENTINEL-1A", "SA"]:
                    json_dict["Platform"][i] = "Sentinel-1A"
                # Sentinel-1B
                elif platform in ["SENTINEL-1B", "SB"]:
                    json_dict["Platform"][i] = "Sentinel-1B"
                # SMAP
                elif platform in ["SMAP", "SP"]:
                    json_dict["Platform"][i] = "SMAP"
                # UAVSAR
                elif platform in ["UAVSAR", "UA", "AIRMOSS"]:
                    json_dict["Platform"][i] = "UAVSAR"
        if "flightdirection" in json_dict:
            for i, flightdirection in enumerate(json_dict["flightdirection"]):
                if flightdirection == None:
                    continue
                # flightdirection in UPPER
                flightdirection = flightdirection.upper()
                # DESCENDING
                if flightdirection in ["D", "DESC", "DESCENDING"]:
                    json_dict["flightdirection"][i] = "DESCENDING"
                #ASCENDING
                elif flightdirection in ["A", "ASC", "ASCENDING"]:
                    json_dict["flightdirection"][i] = "ASCENDING"
        if "polarization" in json_dict:
            for i, polarization in enumerate(json_dict["polarization"]):
                if polarization == None:
                    continue
                # making all results UPPER case, except Dual
                if polarization[0:4].upper() == "DUAL":
                    polarization = "Dual" + polarization[4:].upper()
                else:                
                    polarization = polarization.upper()
                json_dict["polarization"][i] = polarization
        if "collectionname" in json_dict:
            for i, collectionname in enumerate(json_dict["collectionname"]):
                if collectionname == None:
                    continue
                # Note: in url_dict, string is separated by comma: 'Big Island', ' HI'
                # Using the below to match the url string to file string
                # Big Island, HI
                if collectionname in ["Big Island", " HI"]:
                    json_dict["collectionname"][i] = "Big Island, HI"
                # Cascade Volcanoes, CA/OR/WA
                elif collectionname in ["Cascade Volcanoes", " CA/OR/WA"]:
                    json_dict["collectionname"][i] = "Cascade Volcanoes, CA/OR/WA"
        if "beammode" in json_dict:
            for i, beammode in enumerate(json_dict["beammode"]):
                if beammode == None:
                    continue
                # beammode in UPPER case
                beammode = beammode.upper()
                # STANDARD
                if beammode[0:2] == "ST":
                    json_dict["beammode"][i] = "STD"
        return json_dict
    def getUrl(self, test_dict):
        # DONT add these to url. (Used for tester). Add ALL others to allow testing keywords that don't exist
        reserved_keywords = ["title", "print", "api", "type"]
        asserts_keywords = ["expected file","expected code", "expected in file"]

        assert_used = 0 != len([k for k,_ in test_dict.items() if k in asserts_keywords])
        keywords = []
        for key,val in test_dict.items():
            # If it's reserved, move on:
            if key in reserved_keywords or key in asserts_keywords:
                continue
            # IF val is None, just add the key. Else add "key=val"
            if val == None:
                keywords.append(str(key))
            # If you're testing multiple SAME params, add each key-val pair:
            elif isinstance(val, type([])):
                keywords.append(str(key)+"="+",".join(val))
            else:
                keywords.append(str(key)+"="+str(val))
        query = test_dict['api'] + "&".join(keywords)
        return query, assert_used

    def runQuery(self):
        def csvToDict(file_content):
            file_content = csv.reader(StringIO(file_content), delimiter=',')
            file_content = [a for a in file_content]
            # Rotate it counter-clockwise, so that row[0] == key of csv. (based on https://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python)
            rotated_content = list(map(type([]), zip(*file_content)))
            file_content = {}
            for column in rotated_content:
                file_content[column[0]] = column[1:]
            return file_content

        def jsonToDict(json_data):
            # Combine all matching key-value pairs, to-> key: [list of vals]
            file_content = {}
            for result in json_data:
                for key,val in result.items():
                    # Break apart nested lists if needed, (alows to forloop val):
                    val = [val] if not isinstance(val, type([])) else val
                    if key in file_content:
                        for inner_val in val:
                            file_content[key].append(inner_val)
                    else:
                        file_content[key] = []
                        for inner_val in val:
                            file_content[key].append(inner_val)
            return file_content

        h = requests.head(self.query)
        # text/csv; charset=utf-8
        content_type = h.headers.get('content-type').split('/')[1]
        # Take out the "csv; charset=utf-8", without crahsing on things without charset
        content_type = content_type.split(';')[0] if ';' in content_type else content_type
        file_content = requests.get(self.query).content.decode("utf-8")
        # print(file_content)

        ## COUNT / HTML:
        if content_type == "html":
            content_type = "count"
            if file_content == '0\n':
                content_type = "blank count"
        ## CSV
        elif content_type == "csv":
            file_content = csvToDict(file_content)
            blank_csv = {"Granule Name": [],"Platform": [],"Sensor": [],"Beam Mode": [],"Beam Mode Description": [],"Orbit": [],"Path Number": [],"Frame Number": [],"Acquisition Date": [],"Processing Date": [],"Processing Level": [],"Start Time": [],"End Time": [],"Center Lat": [],"Center Lon": [],"Near Start Lat": [],"Near Start Lon": [],"Far Start Lat": [],"Far Start Lon": [],"Near End Lat": [],"Near End Lon": [],"Far End Lat": [],"Far End Lon": [],"Faraday Rotation": [],"Ascending or Descending?": [],"URL": [],"Size (MB)": [],"Off Nadir Angle": [],"Stack Size": [],"Baseline Perp.": [],"Doppler": [],"GroupID":[]}
            if file_content == blank_csv:
                content_type = "blank csv"
        ## DOWNLOAD / PLAIN
        elif content_type == "plain":
            content_type = "download"
            # Check if download script contains this, without granuals in the list:
            match = re.search(r'self\.files\s*=\s*\[\s*\]', str(file_content))
            # If you find it, it's the blank script. If not, There's something there to be downloaded:
            if match:
                content_type = "blank download"
            else:
                content_type = "download"

        ## GEOJSON
        elif content_type == "geojson":
            if file_content == '{\n  "features": [],\n  "type": "FeatureCollection"\n}':
                content_type = "empty geojson"

        ## JSON / JSONLITE / ERROR
        elif content_type == "json":
            file_content = json.loads(file_content)
            ## ERROR
            if "error" in file_content:
                content_type = "error json"
            ## JSONLITE
            elif "results" in file_content:
                file_content = file_content["results"]
                if len(file_content) == 0:
                    content_type = "blank jsonlite"
                else:
                    content_type = "jsonlite"
                    file_content = jsonToDict(file_content)
            ## JSON
            else:
                json_data = file_content[0]
                if json_data == []:
                    content_type = "blank json"
                else:
                    # dictonary-ify file_content to expected format:
                    file_content = jsonToDict(json_data)

        ## KML
        elif content_type == "vnd.google-earth.kml+xml":
            content_type = "kml"
            blank_kml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n<name>ASF Datapool Search Results</name>\n<description>Search Performed: </description>\n<Style id="yellowLineGreenPoly">\n<LineStyle>\n<color>30ff8800</color>\n<width>4</width>\n</LineStyle>\n<PolyStyle>\n<color>7f00ff00</color>\n</PolyStyle>\n</Style>\n</Document>\n</kml>'.replace(" ", "")
            if file_content.replace(" ", "") == blank_kml:
                content_type = "blank kml"
        ## METALINK
        elif content_type == "metalink+xml":
            content_type = "metalink"
            blank_metalink = '<?xml version="1.0"?>\n<metalink xmlns="http://www.metalinker.org/" version="3.0">\n<publisher><name>Alaska Satellite Facility</name><url>http://www.asf.alaska.edu/</url></publisher>\n<files>\n</files>\n</metalink>'.replace(" ","")
            if file_content.replace(" ","") == blank_metalink:
                content_type = "blank metalink"
        return h.status_code, content_type, file_content






################################
## BULK DOWNLOAD SCRIPT TESTS ##
################################
class BULK_DOWNLOAD_SCRIPT_Manager():
    def __init__(self, test_info, bulk_download_path):
        self.cwd = os.path.dirname(os.path.abspath(__file__))
        self.test_info = self.applyDefaultValues(test_info)
        print()
        print(self.test_info["args"])
        print()
        self.bulk_download_path = bulk_download_path
        self.cred_path = "unit_tests/creds_earthdata.yml"

        cookie_jar_path = os.path.join( os.path.expanduser('~'), ".bulk_download_cookiejar.txt")

        if test_info["print"]:
            print("\n Test: {0}".format(test_info["title"]))

        for version in self.test_info["python_version"]:
            if test_info["print"]:
                print()

            # Take out any cookies, make things consistant:
            if os.path.isfile(cookie_jar_path):
                os.remove(cookie_jar_path)

            cmd = "python{0} {1} {2}".format(str(version), self.bulk_download_path, self.test_info["args"])
            if test_info["print"]:
                print("    cmd: {0}".format(cmd))
            bulk_process = pexpect.spawn(cmd, encoding='utf-8', timeout=10, cwd=self.cwd)
            self.run_process_tests(bulk_process)


    def applyDefaultValues(self, test_info):
        def turnValueIntoList(key, test_info, default=[]):
            # if it doesn't even exist, make it the default:
            if key not in test_info:
                test_info[key] = default
            # if it's just one val, turn into a list of that val:
            elif not isinstance(test_info[key], type([])):
                test_info[key] = [ test_info[key] ]
            return test_info

        # args:
        if "args" not in test_info:
            test_info["args"] = ""
        else:
            args = test_info["args"].split(" ")
            for i, arg in enumerate(args):
                if arg.endswith('.metalink') or arg.endswith('.csv'):
                    args[i] = os.path.join(self.cwd, "unit_tests", "Resources", "bulk_download_input", arg)
                    print(args[i])
            test_info["args"] = " ".join(args)
        # expect_in_output:
        test_info = turnValueIntoList("expect_in_output", test_info)
        # print:
        if "print" not in test_info:
            test_info["print"] = False if "expected_outcome" in test_info else True
        # python_version:
        test_info = turnValueIntoList("python_version", test_info, default=[2, 3])
        return test_info




    def run_process_tests(self, bulk_process):
        username, password = self.get_test_creds()
        
        if self.test_info["print"]:
            bulk_process.logfile = sys.stdout

        finished_parsing_commands = False
        file_not_found_hit = False
        unknown_arg_hit = False
        while not finished_parsing_commands:
            # script_output = (int) which element was hit in list:
            script_output = bulk_process.expect([r"No existing URS cookie found, please enter Earthdata username & password:", \
                                                 r"Re-using previous cookie jar.", \
                                                 r"I cannot find the input file you specified", \
                                                 r"Command line argument .* makes no sense, ignoring\."])
            # These could get hit if you pass args to the script, before it finds the cookie:
            if script_output in [0, 1]:
                cookie_exists = script_output
                finished_parsing_commands = True
            elif script_output == 2:
                assert "file_not_found" in self.test_info["expect_in_output"], "Cannot find specified file. Add 'file_not_found' to expect_in_output to pass this check. Test: {0}.".format(self.test_info["title"])
                file_not_found_hit = True
            elif script_output == 3:
                assert "unknown_arg" in self.test_info["expect_in_output"], "Argument(s) make no sense. Add 'unknown_arg' to expect_in_output to pass this check. Test: {0}.".format(self.test_info["title"])
                unknown_arg_hit = True
        # If you state it in expect_in_output, make sure it actually got hit:
        if "file_not_found" in self.test_info["expect_in_output"]:
            assert file_not_found_hit, "'file_not_found' declared in 'expect_in_output', but all the files were found... Test: {0}.".format(self.test_info["title"])
        if "unknown_arg" in self.test_info["expect_in_output"]:
            assert unknown_arg_hit, "'unknown_arg' declared in 'expect_in_output', but all the files were found... Test: {0}.".format(self.test_info["title"])


        # No cookie found:
        if cookie_exists == 0:
            bulk_process.expect(r"Username:")
            bulk_process.sendline(username)
            bulk_process.expect(r"Password \(will not be displayed\):")
            bulk_process.sendline(password)

            # creds_success = (int) which element was hit in list:
            creds_success = bulk_process.expect([r"Username and Password combo was not successful\. Please try again\.", \
                                                 r"New users: you must first log into Vertex and accept the EULA\. In addition, your Study Area must be set", \
                                                 r"attempting to download https:\/\/urs\.earthdata\.nasa\.gov\/profile"])
            if creds_success == 0:
                if self.test_info["print"]:
                    print("RESULT: Invalid Username Password combo")
                if "expected_outcome" in self.test_info:
                    bad_pass_error_msg = "Bad username/password. EarthData Account: {0}. Test: {1}.".format(self.test_info["account"], self.test_info["title"])
                    assert self.test_info["expected_outcome"] == "bad_creds", bad_pass_error_msg
                # No valid cookie, no point on continuing:
                return
            elif creds_success == 1:
                if self.test_info["print"]:
                    print("RESULT: Eula for {0} not checked.".format(self.test_info['account']))
                if "expected_outcome" in self.test_info:
                    # Note: Same header gets returned for both of these. No way to tell them apart atm
                    error_msg = "Cannot download data: Study area / Eula isn't set in profile. EarthData Account: {0}. Test: {1}.".format(self.test_info["account"], self.test_info["title"])
                    assert self.test_info["expected_outcome"] in ["bad_eula", "bad_study_area"], error_msg
                # No way to download data, no point on continuing:
                bulk_process.expect(pexpect.EOF)
                return
        # From here on, you have a cookie:
        # elif cookie_exists == 1:
        if self.test_info["print"]:
            print("RESULT: Able to download data!!")
        bulk_process.expect(r"Download Summary")
        bulk_process.expect(pexpect.EOF)
        # Valid cookie, check download here:



    def get_test_creds(self):
        # Try to open the file, and save the yml:
        try:
            yml_file = open(self.cred_path, "r")
            accounts_dict = yaml.safe_load(yml_file)
        except (OSError, IOError):
            assert False, "Error opening yaml {0}. Does it exist?".format(self.cred_path)
        except (yaml.YAMLError, yaml.MarkedYAMLError) as e:
            assert False, "Error parsing yaml {0}. Error: {1}.".format(self.cred_path, str(e))
        
        # Check if account in yml:
        account = self.test_info["account"]
        if account in accounts_dict:
            try:
                username = accounts_dict[account]["user"]
                password = accounts_dict[account]["pass"]
            except KeyError as e:
                assert False, "Test {0} is not formatted correctly. No user/pass. Error: {1}.".format(self.test_info["title"], str(e))
        else:
            assert False, "Account {0} not found in {1}.".format(account, self.cred_path)
        # Success! heres your user/pass
        return username, password


################
## START MAIN ##
################
# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the @pytest.mark.parametrize:
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__)))
resources_root = os.path.join(project_root, "unit_tests", "Resources")

list_of_tests = []

# Get the tests from all *yml* files:
tests_root = os.path.join(project_root, "**", "test_*.yml")
list_of_tests.extend(helpers.loadTestsFromDirectory(tests_root, recurse=True))

# Same, but with *yaml* files now:
tests_root = os.path.join(project_root, "**", "test_*.yaml")
list_of_tests.extend(helpers.loadTestsFromDirectory(tests_root, recurse=True))


## Stop every bulk_download test from re-requesting the *same* bulk download file fo every test.
# Set key=val as: api_url=script_path for first call, then reuse it:
bulk_download_storage = {}

@pytest.mark.parametrize("test_dict", list_of_tests)
def test_MainManager(test_dict, cli_args):
    test_info = test_dict[0]
    file_config = test_dict[1]

    test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
    helpers.skipTestsIfNecessary(test_info, file_config, cli_args)

    if test_info['type'] == 'WKT':
        test_info['api'] = test_info['api'] + "services/utils/files_to_wkt"
        WKT_Manager(test_info)
    elif test_info['type'] == 'INPUT':
        INPUT_Manager(test_info)
    elif test_info['type'] == 'URL':
        test_info['api'] = test_info['api'] + "services/search/param?"
        URL_Manager(test_info)
    elif test_info['type'] == 'BULK_DOWNLOAD':
        # If you already got the script once, don't do it again:
        if test_info['api'] in bulk_download_storage:
            bulk_download_path = bulk_download_storage[test_info['api']]
        else:
            try:
                url = test_info['api'] + "?filename=Testing"
                r = requests.get(url)
            except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects) as e:
                assert False, "Cannot connect to API: {0}. Error: {1}.".format(url, str(e))
            bulk_download_code = r.content.decode("utf-8")
            # file_name = base_url + ".py" (ie: 127.0.0.1.py)
            bulk_download_path = urllib.parse.urlsplit(test_info['api']).netloc + ".py"
            with open(bulk_download_path, "w+") as f:
                f.write(bulk_download_code)

            # Store it for next time around
            bulk_download_storage[test_info['api']] = bulk_download_path

        BULK_DOWNLOAD_SCRIPT_Manager(test_info, bulk_download_path)
