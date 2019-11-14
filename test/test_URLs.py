
import os, sys, re
from io import StringIO
import csv
# from csv import Error
import json
# from json import JSONDecodeError
import pytest, warnings
import requests
import glob
import itertools
import argparse
from copy import deepcopy
import urllib.parse

# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import conftest as helpers
from CMR import Input

class RunSingleURLFromFile():
    def __init__(self, json_dict, url_api):
        self.query, assert_used = self.getUrlFromParams(json_dict, url_api)
        status_code, file_type, file_content = self.runQuery()

        if "print" not in json_dict:
            json_dict["print"] = False if assert_used else True


        if assert_used:
            if "expected code" in json_dict:
                assert json_dict["expected code"] == status_code, "Status codes is different than expected. Test: {0}. URL: {1}.".format(json_dict["title"], self.query)
            if "expected file" in json_dict:
                    assert json_dict["expected file"] == file_type, "Different file type returned than expected. Test: {0}. URL: {1}.".format(json_dict["title"], self.query)
                    # If you expect it to be a ligit file, and 'file_content' was converted from str to dict:
                    if file_type[0:5] not in ["error", "blank"] and isinstance(file_content, type({})):
                        ### BEGIN TESTING FILE CONTENTS:
                        json_dict = self.parseTestValues(json_dict)
                        file_content = self.renameKeysToStandard(file_content)
                        file_content = self.renameValsToStandard(file_content)
                        # print(json.dumps(json_dict, indent=4, default=str))
                        # IF used in url, IF contained in file's content, check if they match
                        def checkFileContainsExpected(key, url_dict, file_dict):
                            # print(url_dict)
                            # print("CHECKING FILE HERE")
                            # print(file_dict)
                            # print(json.dumps(file_dict, indent=4, default=str))
                            if key in url_dict and key in file_dict:
                                print("HEREEEEEEEEEE")
                                found_in_list = False
                                print("FINDS AND VALIDATES VALUE IN FILE!!!!!")
                                for found_param in file_dict[key]:
                                    for poss_list in url_dict[key]:
                                        if isinstance(poss_list, type([])):
                                            expect_type = type(poss_list[0])
                                            # "found_param" is always a string. Convert it to match
                                            if expect_type(found_param) >= poss_list[0] and expect_type(found_param) <= poss_list[1]:
                                                found_in_list = True
                                                break
                                        else:
                                            expect_type = type(poss_list)
                                            if expect_type(found_param) == poss_list:
                                                found_in_list = True
                                                break
                                    # If inner for-loop found it, break out of this one too:
                                    if found_in_list == True:
                                        break
                                assert found_in_list, key + " declared, but not found in file. Test: {0}".format(json_dict["title"])
                        
                        def checkMinMax(key, url_dict, file_dict):
                            if "min"+key in url_dict and key in file_dict:
                                for value in file_dict[key]:
                                    number_type = type(url_dict["min"+key])
                                    assert number_type(value) >= url_dict["min"+key], "TESTING"
                            if "max"+key in url_dict and key in file_dict:
                                for value in file_dict[key]:
                                    number_type = type(url_dict["max"+key])
                                    assert number_type(value) <= url_dict["max"+key], "TESTING"

                            # elif key[0:4].lower() == "min":
                            #     print("HIT MIN")
                            # elif key[0:4].lower() == "max":
                            #     print("HIT MAX")


                        checkFileContainsExpected("Platform", json_dict, file_content)
                        checkFileContainsExpected("absoluteOrbit", json_dict, file_content)
                        checkFileContainsExpected("asfframe", json_dict, file_content)
                        checkFileContainsExpected("granule_list", json_dict, file_content)
                        checkFileContainsExpected("groupid", json_dict, file_content)
                        checkFileContainsExpected("flightdirection", json_dict, file_content)
                        checkFileContainsExpected("offnadirangle", json_dict, file_content)
                        checkFileContainsExpected("polarization", json_dict, file_content)
                        checkFileContainsExpected("relativeorbit", json_dict, file_content)
                        checkFileContainsExpected("collectionname", json_dict, file_content)
                        checkFileContainsExpected("beammode", json_dict, file_content)

                        checkMinMax("baselineperp", json_dict, file_content)

        # If print wasn't declared, it gets set in parseTestValues:
        if json_dict["print"] == True:
            print()
            print("URL: {0}".format(self.query))
            print("Status Code: {0}. File returned: {1}".format(status_code, file_type))
            print()

    def getUrlFromParams(self, json_dict, url_api):
        # DONT add these to url. (Used for tester). Add ALL others to allow testing keywords that don't exist
        reserved_keywords = ["title", "print"]
        asserts_keywords = ["expected file","expected code", "expected in file"]

        assert_used = 0 != len([k for k,_ in json_dict.items() if k in asserts_keywords])
        keywords = []
        for key,val in json_dict.items():
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
        query = url_api + "&".join(keywords)
        return query, assert_used


    def parseTestValues(self, json_test):
        # Turn string values to lists:
        mutatable_dict = deepcopy(json_test)
        try:
            # Dictionary changes sizes, so check one dict, and make  thechanges to other
            for key, val in json_test.items():
                # The Input.parse* methods all expect a string:
                val = str(val)
                if key.lower() == "absoluteorbit":
                    del mutatable_dict[key]
                    mutatable_dict["absoluteOrbit"] = Input.parse_int_or_range_list(val)
                elif key.lower() == "platform":
                    del mutatable_dict[key]
                    mutatable_dict["Platform"] = Input.parse_string_list(val)
                elif key.lower() in ["frame", "asfframe"]:
                    del mutatable_dict[key]
                    mutatable_dict["asfframe"] = Input.parse_int_or_range_list(val)
                elif key.lower() == "granule_list":
                    del mutatable_dict[key]
                    mutatable_dict["granule_list"] = Input.parse_string_list(val)
                elif key.lower() == "groupid":
                    del mutatable_dict[key]
                    mutatable_dict["groupid"] = Input.parse_string_list(val)
                elif key.lower() == "flightdirection":
                    del mutatable_dict[key]
                    mutatable_dict["flightdirection"] = Input.parse_string_list(val)
                elif key.lower() == "offnadirangle":
                    del mutatable_dict[key]
                    mutatable_dict["offnadirangle"] = Input.parse_float_or_range_list(val)
                elif key.lower() == "polarization":
                    del mutatable_dict[key]
                    val = urllib.parse.unquote_plus(val)
                    mutatable_dict["polarization"] = Input.parse_string_list(val)
                elif key.lower() == "relativeorbit":
                    del mutatable_dict[key]
                    mutatable_dict["relativeorbit"] = Input.parse_int_or_range_list(val)
                elif key.lower() == "collectionname":
                    del mutatable_dict[key]
                    val = urllib.parse.unquote_plus(val)
                    mutatable_dict["collectionname"] = Input.parse_string_list(val)
                elif key.lower() in ["beammode", "beamswath"]:
                    del mutatable_dict[key]
                    mutatable_dict["beammode"] = Input.parse_string_list(val)
                # MIN/MAX veriants
                elif key.lower()[3:] == "baselineperp":
                    del mutatable_dict[key]
                    # Save the min/max key, all lower
                    mutatable_dict[key.lower()[0:3]+"baselineperp"] = Input.parse_float(val)

        except ValueError as e:
            assert False, "Test: {0}. Incorrect parameter: {1}".format(json_test["title"], str(e))
        json_test = mutatable_dict
        # Make each possible value line up with what the files returns:
        json_test = self.renameValsToStandard(json_test)
        return json_test

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
        for key in ["Baseline Perp.", "baselinePerp"]:
            if key in json_dict:
                json_dict["baselineperp"] = json_dict.pop(key)
        return json_dict


    # assumes values are in the form of {key: [value1,value2]}
    def renameValsToStandard(self, json_dict):
        if "Platform" in json_dict:
            itter_copy = deepcopy(json_dict)
            for i, platform in enumerate(itter_copy["Platform"]):
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
                # making all results UPPER case, except Dual
                if polarization[0:4].upper() == "DUAL":
                    polarization = "Dual" + polarization[4:].upper()
                else:                
                    polarization = polarization.upper()
                json_dict["polarization"][i] = polarization
        if "collectionname" in json_dict:
            for i, collectionname in enumerate(json_dict["collectionname"]):
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
                # beammode in UPPER case
                beammode = beammode.upper()
                # STANDARD
                if beammode[0:2] == "ST":
                    json_dict["beammode"][i] = "STD"
                # Standard is different for Radarsat
                # elif beammode in ["STANDARD", "STD"]:
                #     json_dict["beammode"][i] = "STD"
        return json_dict

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




# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the @pytest.mark.parametrize:
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
list_of_tests = []

# Get the tests from all *yml* files:
tests_root = os.path.join(project_root, "test","**","test_*.yml")
list_of_tests.extend(helpers.loadTestsFromDirectory(tests_root, recurse=True))

# Same, but with *yaml* files now:
tests_root = os.path.join(project_root, "test","**","test_*.yaml")
list_of_tests.extend(helpers.loadTestsFromDirectory(tests_root, recurse=True))


@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachURLInYaml(json_test, get_cli_args):
    test_info = json_test[0]
    file_config = json_test[1]

    # Load command line args:
    api_cli = get_cli_args["api"]
    only_run_cli = get_cli_args["only run"]
    dont_run_cli = get_cli_args["dont run"]

    test_info = helpers.moveTitleIntoTest(test_info)

    if test_info == None:
        pytest.skip("Test does not have a title.")

    # If they passed '--only-run val', and val not in test title:
    if only_run_cli != None and only_run_cli.lower() not in test_info["title"].lower():
        pytest.skip("Title of test did not contain --only-run param (case insensitive)")
    # Same, but reversed for '--dont-run':
    if dont_run_cli != None and dont_run_cli.lower() in test_info["title"].lower():
        pytest.skip("Title of test contained --dont-run param (case insensitive)")


    # Default to command line if they used it, else check in the file. (can still be None)
    api_url = api_cli if api_cli != None else file_config['api']
    # Change any keywords for api to the api's url itself:
    api_url = helpers.getAPI(api_url, default="TEST", params="/services/search/param?")

    RunSingleURLFromFile(test_info, api_url)