import requests, urllib     # For talking w/ API
import pytest, warnings     # Tests stuff
import json, csv            # File stuff
import re                   # Opening/Reading the file stuff
from io import StringIO     # Opening/Reading the file stuff
from copy import deepcopy   # For making duplicate dicts

# For timezone/timestamp verification:
from datetime import datetime
from tzlocal import get_localzone
from pytz import timezone

import sys, os              # Path manipulation
this_folder = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(this_folder, ".."))
sys.path.append(project_root)
import CMR.Input as test_input
sys.path.remove(project_root)


class test_URL_Manager():
    def __init__(self, test_info, file_conf, cli_args, test_vars):
        if cli_args["api"] != None:
            test_api = cli_args["api"]
        elif "api" in file_conf:
            test_api = file_conf["api"]
        else:
            assert False, "Endpoint test ran, but '--api' not declared in CLI (test_files_to_wkt).\nCan also add 'default' api to use in yml_tests/pytest_config.yml.\n"
        url_parts = [test_api, test_vars["endpoint"]]
        full_url = '/'.join(s.strip('/') for s in url_parts) # If both/neither have '/' between them, this still joins them correctly
        
        # Get the url string and (bool)if assert was used:
        keywords, assert_used = self.getKeywords(test_info)
        self.query = full_url + "&".join(keywords)

        # Figure out if you should print stuff:
        if "print" not in test_info:
            test_info["print"] = False if assert_used else True

        status_code, content_type, file_content = self.runQuery(test_info["title"])

        if test_info["print"]:
            print()
            print("Test: " + str(test_info["title"]))
            print("API code returned: " + str(status_code))
            print("API file type returned: " + str(content_type))
            print("URL: " + str(self.query))
            print()

        if assert_used:
            self.runAssertTests(test_info, status_code, content_type, file_content)



    def getKeywords(self, test_info):
        # DONT add these to url. (Used for tester). Add ALL others to allow testing keywords that don't exist
        reserved_keywords = ["title", "print", "api", "type", "skip_file_check"]
        asserts_keywords = ["expected file","expected code", "expected in file"]


        assert_used = 0 != len([k for k,_ in test_info.items() if k in asserts_keywords])
        keywords = []
        for key,val in test_info.items():
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
        return keywords, assert_used

    def runQuery(self, title):
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
            try:
                file_content = countToDict(file_content)
            except ValueError as e:
                assert False, "API returned html that was not a count. Test: {0}. URL: {1}.\nHTML Page: \n{2}\n".format(title, self.query, file_content)
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

    def runAssertTests(self, test_info, status_code, content_type, file_content):
        if "expected code" in test_info:
            assert test_info["expected code"] == status_code, "Status codes is different than expected. Test: {0}. URL: {1}.".format(test_info["title"], self.query)
        if "count" in file_content and "maxResults" in test_info:
            assert test_info["maxResults"] >= file_content["count"], "API returned too many results. Test: {0}. URL: {1}.".format(test_info["title"], self.query)
        if "expected file" in test_info:
            assert test_info["expected file"] == content_type, "Different file type returned than expected. Test: '{0}'. URL: {1}.".format(test_info["title"], self.query)
            # If the tester added the override, don't check its contents:
            if "skip_file_check" in test_info and test_info["skip_file_check"] == True:
                return
            # If it's not a valid file, don't check its contents:
            if not isinstance(file_content, type({})) or content_type[0:5] in ["error", "blank"]:
                return
            ### BEGIN TESTING FILE CONTENTS:
            test_info = self.parseTestValues(test_info)
            file_content = self.renameKeysToStandard(file_content)
            file_content = self.renameValsToStandard(file_content)
            # print(json.dumps(test_info, indent=4, default=str))
            # IF used in url, IF contained in file's content, check if they match

            def checkFileContainsExpected(key, test_info, file_dict):
                # print(test_info)
                # print("CHECKING FILE HERE")
                # print(file_dict)
                # print(json.dumps(file_dict, indent=4, default=str))
                if key in test_info and key in file_dict:
                    found_in_list = False
                    for found_param in file_dict[key]:
                        # poss_list is either single "i", or range "[i,j]":
                        for poss_list in test_info[key]:
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
                    assert found_in_list, key + " declared, but not found in file. Test: '{0}'. URL: '{1}'.".format(test_info["title"], self.query)
            
            def checkMinMax(key, test_info, file_dict):
                if "min"+key in test_info and key in file_dict:
                    for value in file_dict[key]:
                        number_type = type(test_info["min"+key])
                        assert number_type(value) >= test_info["min"+key], "Value found smaller than min key. Test: '{0}'. URL: {1}.".format(test_info["title"], self.query)
                if "max"+key in test_info and key in file_dict:
                    for value in file_dict[key]:
                        number_type = type(test_info["max"+key])
                        assert number_type(value) <= test_info["max"+key], "Value found greater than max key. Test: '{0}'. URL: {1}.".format(test_info["title"], self.query)

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


            checkFileContainsExpected("Platform", test_info, file_content)
            checkFileContainsExpected("absoluteOrbit", test_info, file_content)
            checkFileContainsExpected("asfframe", test_info, file_content)
            checkFileContainsExpected("granule_list", test_info, file_content)
            checkFileContainsExpected("groupid", test_info, file_content)
            checkFileContainsExpected("flightdirection", test_info, file_content)
            checkFileContainsExpected("offnadirangle", test_info, file_content)
            checkFileContainsExpected("polarization", test_info, file_content)
            checkFileContainsExpected("relativeorbit", test_info, file_content)
            checkFileContainsExpected("collectionname", test_info, file_content)
            checkFileContainsExpected("beammode", test_info, file_content)
            checkFileContainsExpected("processinglevel", test_info, file_content)
            checkFileContainsExpected("flightline", test_info, file_content)
            checkFileContainsExpected("lookdirection", test_info, file_content)

            # Processing Date (can not validate because it uses a field from CMR not in the API):
            # if "processingdate" in file_content and "processingdate" in test_info:
            #     checkDate(test_info["title"], later_date=file_content["processingdate"], earlier_date=test_info["processingdate"])
            # Start & End:
            if "starttime" in file_content and "start" in test_info:
                checkDate(test_info["title"], later_date=file_content["starttime"], earlier_date=test_info["start"])
            if "starttime" in file_content and "end" in test_info:
                checkDate(test_info["title"], later_date=test_info["end"], earlier_date=file_content["starttime"])

            if "starttime" in file_content and "endtime" in file_content and "season" in test_info:
                checkSeason(test_info["title"], file_content["starttime"], file_content["endtime"], test_info["season"])

            checkMinMax("baselineperp", test_info, file_content)
            checkMinMax("doppler", test_info, file_content)
            checkMinMax("insarstacksize", test_info, file_content)
            checkMinMax("faradayrotation", test_info, file_content)



    def parseTestValues(self, test_info):
        # Turn string values to lists:
        mutatable_dict = deepcopy(test_info)
        try:
            # Dictionary changes sizes, so check one dict, and make  thechanges to other
            for key, val in test_info.items():
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
            assert False, "Test: '{0}'. Incorrect parameter: {1}. URL: {2}.".format(test_info["title"], str(e), self.query)

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
        test_info = mutatable_dict
        # Make each possible value line up with what the files returns:
        test_info = self.renameValsToStandard(test_info)
        return test_info

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
                # Note: in test_info, string is separated by comma: 'Big Island', ' HI'
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

