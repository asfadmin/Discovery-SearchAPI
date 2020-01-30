import os, sys, re, glob
import pytest, warnings
import requests, urllib
import geomet, shapely
import json, csv, yaml
import pexpect

from copy import deepcopy
from io import StringIO
from shutil import copyfile, rmtree
from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone
import defusedxml.minidom as md

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
                warnings.warn(UserWarning("File not found: {0}. File paths start after: '{1}'. (Test: '{2}')".format(poss_path, resources_root, test_dict["title"])))
            else:
                test_wkts.append(test)
        # If you expect to test a file parse, but no files were given:
        if len(test_files) == 0 and "parsed wkt" in test_dict:
            assert False, "Test: '{0}'. 'parsed wkt' declared, but no files were found to parse. Did you mean 'repaired wkt'?".format(test_info["title"])
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
                    assert False, "API did not return the expected message. Test: '{0}'.".format(self.test_dict["title"])
            if "parsed wkt" in self.test_dict:
                if self.content[0] != "{":
                    lhs = geomet.wkt.loads(self.content)
                    rhs = geomet.wkt.loads(self.test_dict["parsed wkt"])
                    assert lhs == rhs, "Parsed wkt returned from API did not match 'parsed wkt'."
                else:
                    assert False, "API did not return a WKT. Test: '{0}'".format(self.test_dict["title"])

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
                    assert shapely.wkt.loads(self.content["wkt"]["wrapped"]) == shapely.wkt.loads(self.test_dict["repaired wkt wrapped"]), "WKT wrapped failed to match the result. Test: '{0}'".format(self.test_dict["title"])
                else:
                    assert False, "WKT not found in response from API. Test: '{0}'. Response: {1}.".format(self.test_dict["title"], self.content)
            if "repaired wkt unwrapped" in self.test_dict:
                if "wkt" in self.content:
                    assert shapely.wkt.loads(self.content["wkt"]["unwrapped"]) == shapely.wkt.loads(self.test_dict["repaired wkt unwrapped"]), "WKT unwrapped failed to match the result. Test: '{0}'".format(self.test_dict["title"])
                else:
                    assert False, "WKT not found in response from API. Test: '{0}'. Response: {1}.".format(self.test_dict["title"], self.content)

            if self.test_dict["check repair"]:
                if "repairs" in self.content:
                    for repair in self.test_dict["repair"]:
                        assert repair in str(self.content["repairs"]), "Expected repair was not found in results. Test: '{0}'. Repairs done: {1}".format(self.test_dict["title"], self.content["repairs"])
                    assert len(self.content["repairs"]) == len(self.test_dict["repair"]), "Number of repairs doesn't equal number of repaired repairs. Test: '{0}'. Repairs done: {1}.".format(self.test_dict["title"],self.content["repairs"])
                else:
                    assert False, "Unexpected WKT returned: {0}. Test: '{1}'".format(self.content, self.test_dict["title"])
            if "repaired error msg" in self.test_dict:
                if "error" in self.content:
                    assert self.test_dict["repaired error msg"] in self.content["error"]["report"], "Got different error message than expected. Test: '{0}'.".format(self.test_dict["title"])
                else:
                    assert False, "Unexpected WKT returned: {0}. Test: '{1}'".format(self.content, self.test_dict["title"])


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
        test_input_file = self.test_dict["input"]
        try:
            hit_exception = False
            val = self.parsers[parser](test_input_file)
        except Exception as e:
            hit_exception = True
            val = str(e)

        if self.should_print:
            print(val)
            print("hit_exception: " + str(hit_exception))
            print()

        if "expected" in self.test_dict:
            assert (self.test_dict["expected"] == val) and (not hit_exception), "CMR INPUT: expected doesn't match output. Test: '{0}'.".format(self.test_dict["title"])
        if "expected error" in self.test_dict:
            assert (self.test_dict["expected error"] in val) and hit_exception, "CMR INPUT: expected error doesn't match output error. Test: '{0}'.".format(self.test_dict["title"])


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
        if "count" in file_content and "maxResults" in test_dict:
            assert test_dict["maxResults"] >= file_content["count"], "API returned too many results. Test: {0}. URL: {1}.".format(test_dict["title"], self.query)
        if "expected file" in test_dict:
            assert test_dict["expected file"] == content_type, "Different file type returned than expected. Test: '{0}'. URL: {1}.".format(test_dict["title"], self.query)
            # If the tester added the override, don't check its contents:
            if "skip_file_check" in test_dict and test_dict["skip_file_check"] == True:
                return
            # If it's not a valid file, don't check its contents:
            if not isinstance(file_content, type({})) or content_type[0:5] in ["error", "blank"]:
                return
            ### BEGIN TESTING FILE CONTENTS:
            test_dict = self.parseTestValues(test_dict)
            file_content = self.renameKeysToStandard(file_content)
            file_content = self.renameValsToStandard(file_content)
            # print(json.dumps(test_dict, indent=4, default=str))
            # IF used in url, IF contained in file's content, check if they match

            def checkFileContainsExpected(key, test_dict, file_dict):
                # print(test_dict)
                # print("CHECKING FILE HERE")
                # print(file_dict)
                # print(json.dumps(file_dict, indent=4, default=str))
                if key in test_dict and key in file_dict:
                    found_in_list = False
                    for found_param in file_dict[key]:
                        # poss_list is either single "i", or range "[i,j]":
                        for poss_list in test_dict[key]:
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
                    assert found_in_list, key + " declared, but not found in file. Test: '{0}'. URL: '{1}'.".format(test_dict["title"], self.query)
            
            def checkMinMax(key, test_dict, file_dict):
                if "min"+key in test_dict and key in file_dict:
                    for value in file_dict[key]:
                        number_type = type(test_dict["min"+key])
                        assert number_type(value) >= test_dict["min"+key], "Value found smaller than min key. Test: '{0}'. URL: {1}.".format(test_dict["title"], self.query)
                if "max"+key in test_dict and key in file_dict:
                    for value in file_dict[key]:
                        number_type = type(test_dict["max"+key])
                        assert number_type(value) <= test_dict["max"+key], "Value found greater than max key. Test: '{0}'. URL: {1}.".format(test_dict["title"], self.query)

            # FOR tz_orig: The timezone the string came from.
            #       Alaska = "US/Alaska", UTC = "UTC", Blank = whatever timezone you're in now
            def convertTimezoneUTC(time, tz_orig=None):
                # Assume if tz_orig is overriden, it's a string of what timezone they want. Else, get whatever timezone you're in
                tz_orig = get_localzone() if tz_orig == None else timezone(tz_orig)

                # If it's a string, convert it to datetime and localize it. 
                # Else it's already datetime, just localize to the timezone:
                if isinstance(time, type("")):
                    # Strip down a string, so it can be used in the format: "%Y-%m-%dT%H:%M:%S"
                    time = time.split(".")[0] # take of any milliseconds. Normally sec.000000
                    time = time[:-1] if time.endswith("Z") else time # take off the 'Z' if it's on the end
                    time = time[:-3] if time.endswith("UTC") else time # take off the 'UTC' if it's on the end
                    # Convert to a datetime object:
                    time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")

                # Set the timezone to where the timestamp came from:
                time = tz_orig.localize(time)
                # Change it to UTC and return it:
                return time.astimezone(timezone("UTC"))

            def checkDate(title, later_date=None, earlier_date=None):
                # Figure out which is the list of dates:
                # (assuming whichever is the list, is loaded from downloads. The other is from yml file)
                if isinstance(later_date, type([])):
                    earlier_date = convertTimezoneUTC(earlier_date)
                    for theDate in later_date:
                        theDate = convertTimezoneUTC(theDate, tz_orig="UTC")
                        assert theDate >= earlier_date, "File has too small of a date. File: {0}, earlier than test date: {1}. Test: '{2}'. URL: {3}.".format(theDate, earlier_date, title, self.query)
                elif isinstance(earlier_date, type([])):
                    later_date = convertTimezoneUTC(later_date)
                    for theDate in earlier_date:
                        theDate = convertTimezoneUTC(theDate, tz_orig="UTC")
                        assert later_date >= theDate, "File has too large of a date. File: {0}, later than test date: {1}. Test: '{2}'. URL: {3}.".format(theDate, later_date, title, self.query)
                else: # Else they both are a single date. Not sure if this is needed, but...
                    earlier_date = convertTimezoneUTC(earlier_date)
                    later_date = convertTimezoneUTC(later_date)
                    later_date >= earlier_date, "Date: {0} is earlier than date {1}. Test: '{2}'".format(later_date, earlier_date, title)

            def checkSeason(title, file_start_dates, file_end_dates, season_list):
                def date_to_nth_day(date):
                    start_of_year = datetime(year=date.year, month=1, day=1)
                    start_of_year = convertTimezoneUTC(start_of_year, tz_orig="UTC")
                    return (date - start_of_year).days + 1

                if len(file_start_dates) == len(file_end_dates):
                    file_dates = zip(file_start_dates, file_end_dates)
                else:
                    assert False, "Error running test! Not same number of start and end dates. Test: '{0}'. URL: '{1}'.".format(title, self.query)
                
                # If it's [300,5], turn it into [[300,365],[1,5]]. Else make it [[x,y]]
                if season_list[0] > season_list[1]:
                    season_list = [ [season_list[0],365],[1,season_list[1]] ]
                else:
                    season_list = [season_list]

                for date in file_dates:
                    # Each year's range is in a different element. 'season=300,5' on a dataset 2017-2019 will add [300-365,1-365,1-5]:
                    days_ranges = []
                    start_season = convertTimezoneUTC(date[0], tz_orig="UTC")
                    end_season = convertTimezoneUTC(date[1], tz_orig="UTC")
                    year_diff = abs(start_season.year - end_season.year)
                    # First check if the product's date takes up an entire year:
                    if year_diff >= 2 or start_season.month <= end_season.month and year_diff >= 1:
                        days_ranges = [[1,365]]
                    else:
                        # Convert start/end points to ints:
                        start = date_to_nth_day(start_season)
                        end = date_to_nth_day(end_season)
                        # Check if both dates exist in the same calendar year:
                        if year_diff == 0:
                            days_ranges.append([start,end])
                        # append both halfs of the range:
                        else:
                            days_ranges.append([start, 365])
                            days_ranges.append([1, end])

                    # days_ranges is populated. Make sure it lines up with what you asked for:
                    season_range_hit = False
                    for season in season_list:
                        for the_range in days_ranges:
                            # If either boundry in the file is in what you ask for in the season list, you pass:
                            if (season[0] <= the_range[0] <= season[1]) or (season[0] <= the_range[1] <= season[1]):
                                season_range_hit = True
                                break

                    assert season_range_hit, "Seasons not found in file. file ranges: {0}. yml range: {1}. Test: {2}. URL: {3}.".format(days_ranges, season_list, title, self.query)


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
            checkFileContainsExpected("processinglevel", test_dict, file_content)
            checkFileContainsExpected("flightline", test_dict, file_content)
            checkFileContainsExpected("lookdirection", test_dict, file_content)

            # Processing Date (can not validate because it uses a field from CMR not in the API):
            # if "processingdate" in file_content and "processingdate" in test_dict:
            #     checkDate(test_dict["title"], later_date=file_content["processingdate"], earlier_date=test_dict["processingdate"])
            # Start & End:
            if "starttime" in file_content and "start" in test_dict:
                checkDate(test_dict["title"], later_date=file_content["starttime"], earlier_date=test_dict["start"])
            if "starttime" in file_content and "end" in test_dict:
                checkDate(test_dict["title"], later_date=test_dict["end"], earlier_date=file_content["starttime"])

            if "starttime" in file_content and "endtime" in file_content and "season" in test_dict:
                checkSeason(test_dict["title"], file_content["starttime"], file_content["endtime"], test_dict["season"])

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
                # The Input.parse* methods all expect a string. API automatically decodes it too:
                val = urllib.parse.unquote_plus(str(val))
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
                    mutatable_dict["polarization"] = test_input.parse_string_list(val)
                elif key.lower() == "relativeorbit":
                    del mutatable_dict[key]
                    mutatable_dict["relativeorbit"] = test_input.parse_int_or_range_list(val)
                elif key.lower() == "collectionname":
                    del mutatable_dict[key]
                    mutatable_dict["collectionname"] = test_input.parse_string_list(val)
                elif key.lower() in ["beammode", "beamswath"]:
                    del mutatable_dict[key]
                    mutatable_dict["beammode"] = test_input.parse_string_list(val)
                elif key.lower() == "processinglevel":
                    del mutatable_dict[key]
                    mutatable_dict["processinglevel"] = test_input.parse_string_list(val)
                elif key.lower() == "flightline":
                    del mutatable_dict[key]
                    mutatable_dict["flightline"] = test_input.parse_string_list(val)
                elif key.lower() == "lookdirection":
                    del mutatable_dict[key]
                    mutatable_dict["lookdirection"] = test_input.parse_string_list(val)
                # elif key.lower() == "processingdate":
                #     del mutatable_dict[key]
                #     mutatable_dict["processingdate"] = test_input.parse_date(val.replace("+", " "))
                elif key.lower() == "start":
                    del mutatable_dict[key]
                    mutatable_dict["start"] = test_input.parse_date(val.replace("+", " "))
                elif key.lower() == "end":
                    del mutatable_dict[key]
                    mutatable_dict["end"] = test_input.parse_date(val.replace("+", " "))
                elif key.lower() == "season":
                    del mutatable_dict[key]
                    mutatable_dict["season"] = test_input.parse_int_list(val)
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
            assert False, "Test: '{0}'. Incorrect parameter: {1}. URL: {2}.".format(test_dict["title"], str(e), self.query)

        # If start is larger than end, swap them:
        if "start" in mutatable_dict and "end" in mutatable_dict:
            start = datetime.strptime(mutatable_dict["start"], "%Y-%m-%dT%H:%M:%SZ")
            end = datetime.strptime(mutatable_dict["end"], "%Y-%m-%dT%H:%M:%SZ")
            if start > end:
                tmp = mutatable_dict["start"]
                mutatable_dict["start"] = mutatable_dict["end"]
                mutatable_dict["end"] = tmp
        # If skip_file_check not declared, default to False:
        if "skip_file_check" not in mutatable_dict:
            mutatable_dict["skip_file_check"] = False
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
        ### min/max FaradayRotation:
        for key in ["faradayRotation", "Faraday Rotation"]:
            if key in json_dict:
                json_dict["faradayrotation"] = json_dict.pop(key)
        ### processingLevel:
        for key in ["Processing Level", "processingLevel"]:
            if key in json_dict:
                json_dict["processinglevel"] = json_dict.pop(key)
        ### flightLine:
        if "flightLine" in json_dict:
            json_dict["flightline"] = json_dict.pop("flightLine")
        ### lookDirection:
        if "lookDirection" in json_dict:
            json_dict["lookdirection"] = json_dict.pop("lookDirection")
        ### processingDate:
        # for key in ["Processing Date", "processingDate"]:
        #     if key in json_dict:
        #         json_dict["processingdate"] = json_dict.pop(key)
        ### start & end
        for key in ["Start Time", "startTime"]:
            if key in json_dict:
                json_dict["starttime"] = json_dict.pop(key)
        for key in ["End Time", "stopTime"]:
            if key in json_dict:
                json_dict["endtime"] = json_dict.pop(key)
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
                # Sir-C
                elif platform in ["SIR-C"]:
                    del json_dict["Platform"][i]
                    json_dict["Platform"].append("STS-59")
                    json_dict["Platform"].append("STS-68")
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
        if "lookdirection" in json_dict:
            for i, lookdirection in enumerate(json_dict["lookdirection"]):
                if lookdirection == None:
                    continue
                lookdirection = lookdirection.upper()
                #LEFT
                if lookdirection in ["L", "LEFT"]:
                    json_dict["lookdirection"][i] = "LEFT"
                #RIGHT
                elif lookdirection in ["R", "RIGHT"]:
                    json_dict["lookdirection"][i] = "RIGHT"
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
                # Note: in test_dict, string is separated by comma: 'Big Island', ' HI'
                # Using the below to match the url string to file string
                # Big Island, HI
                if collectionname in ["Big Island", " HI"]:
                    json_dict["collectionname"][i] = "Big Island, HI"
                # Cascade Volcanoes, CA/OR/WA
                elif collectionname in ["Cascade Volcanoes", " CA/OR/WA"]:
                    json_dict["collectionname"][i] = "Cascade Volcanoes, CA/OR/WA"
                # Permafrost Sites, AK
                elif collectionname in ["Permafrost Sites", "AK"]:
                    json_dict["collectionname"][i] = "Permafrost Sites, AK"
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
        reserved_keywords = ["title", "print", "api", "type", "skip_file_check"]
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
        def countToDict(html):
            count = int(html.rstrip())
            return {"count": count}

        def csvToDict(file_content):
            file_content = csv.reader(StringIO(file_content), delimiter=',')
            file_content = [a for a in file_content]
            # Rotate it counter-clockwise, so that row[0] == key of csv. (based on https://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python)
            rotated_content = list(map(type([]), zip(*file_content)))
            file_content = {}
            for column in rotated_content:
                file_content[column[0]] = column[1:]
            file_content["count"] = len(file_content["Platform"])
            return file_content
        
        def downloadToDict(bulk_download_file):
            # Grab everything in the self.files field of the download script:
            files = re.search(r'self.files\s*=\s*\[.*?\]', bulk_download_file, re.DOTALL)
            if files == None:
                assert False, "Problem reading download script! URL: {0}. File: {1}.".format(self.query, bulk_download_file)
            # Parse out each file-names, and make each one a str in a list:
            files = re.findall('"(.*?)"', files.group(0))
            # add the fields and return:
            file_content = {}
            file_content["count"] = len(files)
            file_content["files"] = files
            return file_content

        def jsonToDict(json_data):
            # Combine all matching key-value pairs, to-> key: [list of vals]
            file_content = {}
            count = 0
            for result in json_data:
                count += 1
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
            file_content["count"] = count
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
            # They return a number in the html. Convert to a real int:
            file_content = countToDict(file_content)
            if file_content["count"] == 0:
                content_type = "blank count"
            else:
                content_type = "count"
        ## CSV
        elif content_type == "csv":
            file_content = csvToDict(file_content)
            if file_content["count"] == 0:
                content_type = "blank csv"
        ## DOWNLOAD / PLAIN
        elif content_type == "plain":
            file_content = downloadToDict(file_content)
            # how many granules are in the script:
            if file_content["count"] == 0:
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



#######################
## DATE PARSE TESTS ##
#######################
class DATE_PARSE_Manager():
    def __init__(self, test_dict):
        #Get the url string and if assert was used:
        self.query, assert_used = self.getUrl(test_dict)
        status_code, content_type, file_content = self.runQuery()

        if assert_used:
            self.runAssertTests(status_code, test_dict, file_content)


    def getUrl(self, test_dict):
        #DONT add these to url. (Used for tester.)
        reserved_keywords = ["title", "print", "api", "type"]
        asserts_keywords = ["expected file", "expected error", "expected code"]

        assert_used = 0 != len([k for k,_ in test_dict.items() if k in asserts_keywords])
        keywords = []
        for key,val in test_dict.items():
            # If it's reserved, move on:
            if key in reserved_keywords or key in asserts_keywords:
                continue
            # If blank, add key with no value
            if val == None:
                keywords.append(str(key)+"=")
            # Otherwise, add key and value pair to url
            else:
                keywords.append(str(key)+"="+str(val))
        query = test_dict['api'] + "&".join(keywords)
        return query, assert_used

    def runQuery(self):
        
        h = requests.head(self.query)
        # text/csv; charset=utf-8
        content_type = h.headers.get('content-type').split("/")[1]
        # Take out the "csv; charset=utf-8", without crahsing on things without charset
        file_content = requests.get(self.query).content.decode("utf-8")

        if content_type == "json":
            file_content = json.loads(file_content)
            if "error" in file_content:
                content_type = "error json"
            elif "parsed" in file_content:
                content_type = jsonlite
                file_content

        return h.status_code, content_type, file_content

    def runAssertTests(self,status_code, test_dict, file_content):
        assert status_code == 200, "API returned code {0}".format(status_code)
        if "expected error" in test_dict:
            if "error" in file_content:
                assert test_dict["expected error"].lower() in str(file_content).lower(), "API returned a different error than expected. Test: '{0}'.".format(test_dict["title"])
            else:
                assert False, "API parsed value when validation error expected. Test: '{0}'.".format(test_dict["title"])
        if "expected date" in test_dict:
            if "date" in file_content:
                try:
                    time = datetime.strptime(file_content["date"]["parsed"], "%Y-%m-%dT%H:%M:%SZ")
                except ValueError as e:
                    assert False, "API did not return the a date. Error Message: {1} Test: '{0}'.".format(test_dict["title"], str(e))
            else: 
                assert False, "API returned an unexpected parsing error. Test: '{0}'.".format(test_dict["title"])



################################
## BULK DOWNLOAD SCRIPT TESTS ##
################################
class BULK_DOWNLOAD_SCRIPT_Manager():
    def __init__(self, test_info):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.root_dir, "unit_tests", "Resources", "bulk_download_output")
        # also populates self.bulk_download_code:
        self.test_info = self.applyDefaultValues(test_info)
        bulk_download_path = self.getBulkDownloadFromAPI(test_info)

        self.cred_path = os.path.join(self.root_dir, "unit_tests", "creds_earthdata.yml")
        cookie_jar_path = os.path.join( os.path.expanduser('~'), ".bulk_download_cookiejar.txt")

        if self.test_info["print"]:
            print("\n Test: '{0}'".format(self.test_info["title"]))
            print(" --- Number of expected downloads: {0}.".format(len(self.test_info["files"])))

        for version in self.test_info["python_version"]:
            # Take out any files from last test, make things consistant:
            if os.path.isfile(cookie_jar_path):
                os.remove(cookie_jar_path)
            for file in os.listdir(self.output_dir):
                file = os.path.join(self.output_dir, file)
                os.remove(file)

            # Craft the command for both runs:
            cmd = 'python{0} "{1}" {2}'.format(str(version), bulk_download_path, self.test_info["args"])
            if test_info["print"]:
                print("\n --- cmd: {0}".format(cmd))

            try:
                # Do the optional run first. All the asserts *always* happen in the second run then:
                if test_info["test_on_second_run"] == True:
                    bulk_process = pexpect.spawn(cmd, encoding='utf-8', timeout=test_info["timeout"], cwd=self.output_dir)
                    self.run_process_tests(bulk_process, optional_run=True)
                
                # Create files here, to represent files not being completed w/ the first script:
                if "create_files" in test_info:
                    for create_me in test_info["files"]:
                        if test_info["print"] == True:
                            print(" --- Creating file: " + str(create_me))
                        create_me = os.path.join(self.output_dir, create_me)
                        f = open(create_me, "w+")
                        f.close()

                # Run the script for real now, and make sure it does what you're expecting this time:
                bulk_process = pexpect.spawn(cmd, encoding='utf-8', timeout=test_info["timeout"], cwd=self.output_dir)
                self.run_process_tests(bulk_process)            
            except pexpect.exceptions.TIMEOUT:
                assert False, "Test ran out of time! Set 'timeout' in test. (Can be Null to disable, or # seconds). Test: '{0}'.".format(test_info["title"])
        # os.remove(bulk_download_path)



    def applyDefaultValues(self, test_info):
        # Lets tester put in single value or list, and it always becomes a list.
        # if default=None, it won't add the key if it's not already there.
        def turnValueIntoList(key, test_info, default=None):
            # if it doesn't even exist, make it the default:
            if key not in test_info:
                if default != None:
                    test_info[key] = default
                return test_info
            # if it's just one val, turn into a list of that val:
            elif not isinstance(test_info[key], type([])):
                test_info[key] = [ test_info[key] ]
            return test_info
        # NOTE: \/ Keys in alphabetical order: \/ 
        # args / files:
        test_info["files"] = []
        if "args" not in test_info:
            test_info["args"] = ""
        else:
            args = test_info["args"].split(" ")
            for i, arg in enumerate(args):
                if arg.endswith('.metalink') or arg.endswith('.csv'):
                    args[i] = os.path.join(self.root_dir, "unit_tests", "Resources", "bulk_download_input", arg)
                    # List of files to check they get actually downloaded later:
                    test_info["files"].extend(self.getProductNamesFromFile(args[i]))
            test_info["args"] = " ".join(args)
        # create_files:
        test_info = turnValueIntoList("create_files", test_info)
        # expect_in_output:
        test_info = turnValueIntoList("expect_in_output", test_info)
        if "expect_in_output" in test_info:
            for expected in test_info["expect_in_output"]:
                whitelist = ["bad_url", "cookie_existed", "file_not_found", "file_exists", "file_incomplete", "unknown_arg"]
                assert expected in whitelist, "Test parsing error: Unknown value for 'expect_in_output'. Test: '{0}'.".format(test_info["title"])
        # expected_outcome:
        if "expected_outcome" in test_info:
            whitelist = ["success", "bad_creds", "bad_eula", "bad_download_perms", "bad_study_area"]
            assert test_info["expected_outcome"] in whitelist, "Test parsing error: Unknown value for 'expected_outcome'. Test: '{0}'.".format(test_info["title"])
        # print:
        if "print" not in test_info:
            # If any of this list is in test_info, don't print by default:
            used_assertion = len([i for i in ["expected_outcome", "expect_in_output", "inject_output"] if i in test_info]) != 0
            test_info["print"] = not used_assertion
        # products / files:
        test_info = turnValueIntoList("products", test_info)
        # each product is in the form: "http://foo.com/bar.txt", JUST get the bar.txt and extend the list:
        if "products" in test_info:
            test_info["files"].extend([product.split("/")[-1] for product in test_info["products"]])
        # python_version:
        test_info = turnValueIntoList("python_version", test_info, default=[2, 3])
        # skip_file_check:
        if "skip_file_check" not in test_info:
            test_info["skip_file_check"] = False
        # test_on_second_run:
        if "test_on_second_run" not in test_info:
            test_info["test_on_second_run"] = False
        # timeout:
        if "timeout" not in test_info:
            test_info["timeout"] = 10
        elif isinstance(test_info["timeout"], type("")) and test_info["timeout"].lower() == "none": # elif they passed the string "None" instead of Null in yml
            test_info["timeout"] = None
        return test_info

    def getProductNamesFromFile(self, path):
        if not os.path.isfile(path):
            return []
        if path.endswith('.metalink'):
            with open(path, "r") as file:
                xml_str = file.read()
            try:
                xml_root = md.parseString(xml_str, forbid_dtd=True)
            except Exception as e:  
                return []
            products = xml_root.getElementsByTagName("file")
            products = [product.getAttribute("name") for product in products]
        elif path.endswith('.csv'):
            with open(path, "r") as file:
                csv_str = file.read()
            csv_obj = csv.reader(StringIO(csv_str), delimiter=',')
            csv_obj = [a for a in csv_obj]
            csv_obj = list(map(type([]), zip(*csv_obj)))
            file_content = {}
            for column in csv_obj:
                file_content[column[0]] = column[1:]
            products = file_content["URL"]
            # turn http://foo.com/bar.txt to bar.txt
            products = [product.split("/")[-1] for product in products]
        else:
            assert False, "Test Error: Unknown filetype!! Path: '{0}'.".format(path)
        return products


    def getBulkDownloadFromAPI(self, test_info):
        url = test_info['api'] + "?filename=Testing"
        if "products" in test_info and len(test_info["products"]) > 0:
            url += "&products=" + ",".join(test_info["products"])
        try:
            r = requests.get(url)
        except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects) as e:
            assert False, "Cannot connect to API: {0}. Error: {1}.".format(url, str(e))
        self.bulk_download_code = r.content.decode("utf-8")
        tmp_bulk_download_path = os.path.join(self.root_dir, "bulk_download_testing.py")
        with open(tmp_bulk_download_path, "w+") as f:
            f.write(self.bulk_download_code)

        return tmp_bulk_download_path


    def run_process_tests(self, bulk_process, optional_run=False):
        username, password = self.get_test_creds()
        
        if self.test_info["print"]:
            print("Script Output:")
            if optional_run:
                print("   > Optional run:")
            else:
                print("   > Normal testing run:")
            bulk_process.logfile = sys.stdout

        if not optional_run and "products" in self.test_info:
            for product in self.test_info["products"]:
                product = urllib.parse.unquote_plus(product)
                assert product in urllib.parse.unquote_plus(self.bulk_download_code), "Product {0} was not found inside bulk download script. Test: '{1}'.".format(product, self.test_info["title"])

        file_not_found_hit = False
        unknown_arg_hit = False
        inject_hit = False
        
        # Figure out what the file might return. Add possible injection outputs if needed:
        possible_file_outputs = [r"No existing URS cookie found, please enter Earthdata username & password:", \
                                 r"Re-using previous cookie jar.", \
                                 r"I cannot find the input file you specified", \
                                 r"Command line argument .* makes no sense, ignoring\."]
        if "inject_output" in self.test_info:
            possible_file_outputs.append(self.test_info["inject_output"])

        while True:
            # script_output = (int) which element was hit in list:
            script_output = bulk_process.expect(possible_file_outputs)
            # These could get hit if you pass args to the script, before it finds the cookie:
            if script_output in [0,1]:
                cookie_existed = False if script_output == 0 else True
                break
            # These mean you're not done with the input, do another loop around:
            elif script_output == 2:
                file_not_found_hit = True
            elif script_output == 3:
                unknown_arg_hit = True
            # Can get hit if "inject_output" is used in test:
            elif script_output == 4:
                inject_hit = True

        # If you state it in expect_in_output, make sure it actually got hit. If you *didn't* state it, make sure it didn't happen too:
        if not optional_run and "expect_in_output" in self.test_info:
            # Check if you were supposed to hit the warning messages or not:
            assert ("file_not_found" in self.test_info["expect_in_output"]) == file_not_found_hit, "File(s){0} found. {1} 'file_not_found' to 'expect_in_output' if this is expected. Test: '{2}'.".format(" not" if file_not_found_hit else "", "Add" if file_not_found_hit else "Remove", self.test_info["title"])
            assert ("unknown_arg" in self.test_info["expect_in_output"]) == unknown_arg_hit, "Unknown arg(s){0} found. {1} 'unknown_arg' to 'expect_in_output' if this is expected. Test: '{2}'.".format(" not" if unknown_arg_hit else "", "Add" if unknown_arg_hit else "Remove", self.test_info["title"])
            # Check if you wanted to find a cookie or not:
            assert ("cookie_existed" in self.test_info["expect_in_output"]) == cookie_existed, "Cookie{0} found. {1} 'cookie_existed' to 'expect_in_output' if this is expected. Test: '{2}'.".format("" if cookie_existed else " not", "Remove" if cookie_existed else "Add", self.test_info["title"])
        if not optional_run and "inject_output" in self.test_info:
            assert not inject_hit, "Code from 'products' was executed! Test: '{0}'.".format(self.test_info["title"])
        # No cookie found:
        if cookie_existed == False:
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
                    bad_pass_error_msg = "Bad username/password. EarthData Account: {0}. Test: '{1}'.".format(self.test_info["account"], self.test_info["title"])
                    assert self.test_info["expected_outcome"] == "bad_creds", bad_pass_error_msg
                # Can't validate user, no point on continuing:
                # Note: NOT EoF. The script will ask you for your password again
                return
            elif creds_success == 1:
                if self.test_info["print"]:
                    print("RESULT: Eula for '{0}' not checked.".format(self.test_info['account']))
                if "expected_outcome" in self.test_info:
                    # Note: Same header gets returned for both of these. No way to tell them apart atm
                    error_msg = "Cannot download data: Study area / Eula isn't set in profile. EarthData Account: {0}. Test: '{1}'.".format(self.test_info["account"], self.test_info["title"])
                    assert self.test_info["expected_outcome"] in ["bad_eula", "bad_study_area"], error_msg
                # No way to download data, no point on continuing:
                bulk_process.expect(pexpect.EOF)
                return
            elif creds_success == 2:
                # You got a cookie, good to go
                pass
        # From here on, you have a cookie:
        # elif cookie_existed == 1:
        download_existed = False
        download_incomplete = False
        download_bad_url = False
        while True:

            output = bulk_process.expect([ r"Download Summary", \
                                           r"Download file .* exists!", \
                                           r"Found .* but it wasn't fully downloaded\. Removing file and downloading again\.", \
                                           r"URL Error \(from GET\): .* Name or service not known", \
                                           r"HTTP Error: (?!401|403)", \
                                           r"HTTP Error: 401", \
                                           r"HTTP Error: 403"])
            # Success! You got data:
            if output == 0:
                if self.test_info["print"]:
                    print("RESULT: Able to download data!!")
                if "expected_outcome" in self.test_info:
                    assert self.test_info["expected_outcome"] == "success", "Test was not supposed to be able to download data, but it can... Account: {0}. Test: '{1}'.".format(self.test_info["account"], self.test_info["title"])
                break
            # One of the downloads already existed:
            elif output == 1:
                download_existed = True
            # One of the downloads wern't successful the last run:
            elif output == 2:
                download_incomplete = True
            # One of the download url's is down / doesn't exist:
            elif output == 3:
                download_bad_url = True
            # Hit this message the last time datapool was down, for the DB upgrade:
            elif output == 4:
                assert False, "Data is not available. (Datapool down?). Test: '{0}'. Error: '{1}'. Account: '{2}'.".format(self.test_info["title"], bulk_process.after, self.test_info["account"])
            elif output == 5:
                if self.test_info["print"]:
                    print("RESULT: Bad permissions to download data!")
                if "expected_outcome" in self.test_info:
                    assert self.test_info["expected_outcome"] == "bad_download_perms", "Account: {0}, lacks the permissions to download this data. Change 'expected_outcome' to 'bad_download_perms' to pass. Test: '{1}'.".format(self.test_info["account"], self.test_info["title"])
                # Bad account hit. No files to test. Just return:
                bulk_process.expect(pexpect.EOF)
                return
            elif output == 6:
                if self.test_info["print"]:
                    print("RESULT: HTTP 403. You found out how to hit it!! Not sure if possible yet.")
                assert False, "API Returned 403. TODO: Find out what causes this and add tests for it..."
            else:
                assert False, "TESTING ERROR: output is too high, no idea what to expect."



        # Script complete, check your downloads:
        if not optional_run and "expect_in_output" in self.test_info:
            assert ("file_exists" in self.test_info["expect_in_output"]) == download_existed
            assert ("file_incomplete" in self.test_info["expect_in_output"]) == download_incomplete
            assert ("bad_url" in self.test_info["expect_in_output"]) == download_bad_url

        # If the files should exist, check the downloads:        
        if not optional_run and self.test_info["skip_file_check"] == False:
            # get all files from the output dir into one list:
            downloaded_files = os.path.join(self.output_dir, "*")
            downloaded_files = glob.glob(downloaded_files)
            downloaded_files = [os.path.basename(file) for file in downloaded_files]
            # Remove duplicate files, because the same file might be in both 'args' and 'products' param:
            required_files = list(set(self.test_info["files"]))
            # Check downloaded_files against required_files:
            for file in required_files:
                assert file in downloaded_files, "File not found. File: {0}, Test: '{1}'".format(file, self.test_info["title"])
            assert len(required_files) == len(downloaded_files), "Number of files don't line up with what's expected. Test: '{0}'.".format(self.test_info["title"])

        # for file in self.test_info["expected_files"]:
        #     assert file in downloaded_files, "Product: {0} Not found in downloaded files dir. Test: '{1}'.".format(file,self.test_info["title"])
        bulk_process.expect(pexpect.EOF)


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


# Get all yml and yaml files:
all_tests = helpers.loadTestsFromDirectory(project_root, recurse=True)

@pytest.mark.serial
@pytest.mark.parametrize("tests", all_tests["BULK_DOWNLOAD"])
def test_bulkDownload_script(tests, cli_args):
    test_info = tests[0]
    file_config = tests[1]
    test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
    helpers.skipTestsIfNecessary(test_info, file_config["yml name"], cli_args) 
    BULK_DOWNLOAD_SCRIPT_Manager(test_info)

@pytest.mark.parallel
@pytest.mark.parametrize("tests", all_tests["INPUT"])
def test_inputs(tests, cli_args):
    test_info = tests[0]
    file_config = tests[1]
    test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
    helpers.skipTestsIfNecessary(test_info, file_config["yml name"], cli_args)
    INPUT_Manager(test_info)

@pytest.mark.parallel
@pytest.mark.parametrize("tests", all_tests["URL"])
def test_urls(tests, cli_args):
    test_info = tests[0]
    file_config = tests[1]
    test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
    helpers.skipTestsIfNecessary(test_info, file_config["yml name"], cli_args)
    test_info['api'] = test_info['api'] + "services/search/param?"
    print()
    print(test_info)
    print()
    URL_Manager(test_info)

@pytest.mark.parallel
@pytest.mark.parametrize("tests", all_tests["WKT"])
def test_wkts(tests, cli_args):
    test_info = tests[0]
    file_config = tests[1]
    test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
    helpers.skipTestsIfNecessary(test_info, file_config["yml name"], cli_args)
    test_info['api'] = test_info['api'] + "services/utils/files_to_wkt"
    WKT_Manager(test_info)

@pytest.mark.parallel
@pytest.mark.parametrize("tests", all_tests["DATE_PARSE"])
def test_dates(tests, cli_args):
    test_info = tests[0]
    file_config = tests[1]
    test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
    helpers.skipTestsIfNecessary(test_info, file_config["yml name"], cli_args)
    test_info['api'] = test_info['api'] + "services/utils/date?"
    print(test_info)
    DATE_PARSE_Manager(test_info)



# @pytest.mark.parametrize("test_dict", list_of_tests)
# def test_MainManager(test_dict, cli_args):
#     test_info = test_dict[0]
#     file_config = test_dict[1]

#     test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
#     helpers.skipTestsIfNecessary(test_info, file_config, cli_args)

#     if test_info['type'] == 'WKT':
#         test_info['api'] = test_info['api'] + "services/utils/files_to_wkt"
#         WKT_Manager(test_info)
#     elif test_info['type'] == 'INPUT':
#         INPUT_Manager(test_info)
#     elif test_info['type'] == 'URL':
#         test_info['api'] = test_info['api'] + "services/search/param?"
#         URL_Manager(test_info)
#     elif test_info['type'] == 'BULK_DOWNLOAD':
#         BULK_DOWNLOAD_SCRIPT_Manager(test_info)
