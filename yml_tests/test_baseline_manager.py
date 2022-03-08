import requests, urllib     # For talking w/ API
import json, csv            # File stuff
import re                   # Opening/Reading the file stuff
from io import StringIO     # Opening/Reading the file stuff
from copy import deepcopy   # For making duplicate dicts

from SearchAPI.CMR import Input as test_input

class test_baseline():
    def __init__(self, **args):

        test_info = args["test_info"]
        api_info = args["config"].getoption("--api")
        test_api = api_info["this_api"]


        url_parts = [test_api, args["test_type_vars"]["endpoint"]+"?"]
        full_url = '/'.join(s.strip('/') for s in url_parts) # If both/neither have '/' between them, this still joins them correctly

        # If you're overriding if you want to show the maturity:
        if "use_maturity" in test_info:
            use_cmr_maturity = test_info["use_maturity"]
        # Defalut use it, if you're not running against a prod api:
        else:
            use_cmr_maturity = api_info["flexible_maturity"]

        # Get the url string and (bool)if assert was used:
        keywords, assert_used = self.getKeywords(test_info)
        if use_cmr_maturity:
            keywords.append("maturity=" + args["test_type_vars"]["maturity"])
        self.query = full_url + "&".join(keywords)
        # I replace '{0}' with itself, so that you can format that in later, and everything else is populated already:
        self.error_msg = "Reason: {0}\n - URL: '{1}'".format("{0}",self.query)

        # Figure out if you should print stuff:
        if "print" not in test_info:
            test_info["print"] = not assert_used

        status_code, content_type, file_content = self.runQuery()

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
        reserved_keywords = ["title", "print", "skip_file_check", "maturity", "use_maturity"]
        asserts_keywords = ["expected file","expected code"]

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

    def runQuery(self):
        def countToDict(html):
            try:
                count = int(html.rstrip())
            except ValueError:
                assert False, self.error_msg.format("API returned html that was not a count. (Error page?) HTML Page: \n{0}\n".format(file_content))
            return { "count": count }

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
        content_header = h.headers.get('content-type')
        file_content = requests.get(self.query).content.decode("utf-8")
        # text/csv; charset=utf-8
        try:
            content_type = content_header.split('/')[1]
        except AttributeError:
            assert False, self.error_msg.format("Header is not formatted as expected. Header: {0}. File Content: \n{1}\n".format(content_header, file_content))
        # Take out the "csv; charset=utf-8", without crahsing on things without charset
        content_type = content_type.split(';')[0] if ';' in content_type else content_type

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

    def runAssertTests(self, test_info, status_code, content_type, file_content):
        if "expected code" in test_info:
            assert test_info["expected code"] == status_code, self.error_msg.format("Status codes is different than expected.")
        if "expected file" in test_info:
            assert test_info["expected file"] == content_type, self.error_msg.format("Different file type returned than expected.")
            # If the tester added the override, don't check its contents:
            if "skip_file_check" in test_info and test_info["skip_file_check"] == True:
                return
            # If it's not a valid file, don't check its contents:
            if not isinstance(file_content, type({})) or content_type[0:5] in ["error", "blank"]:
                return
            ### BEGIN TESTING FILE CONTENTS:
            test_info = self.parseTestValues(test_info)
            file_content = self.renameKeysToStandard(file_content)
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
                    assert found_in_list, self.error_msg.format(key + " declared, but not found in file.")

            checkFileContainsExpected("processinglevel", test_info, file_content)

    def parseTestValues(self, test_info):
        # Turn string values to lists:
        mutatable_dict = deepcopy(test_info)
        try:
            # Dictionary changes sizes, so check one dict, and make  thechanges to other
            for key, val in test_info.items():
                # The Input.parse* methods all expect a string. API automatically decodes it too:
                val = urllib.parse.unquote_plus(str(val))
                if key.lower() == "processinglevel":
                    del mutatable_dict[key]
                    mutatable_dict["processinglevel"] = test_input.parse_string_list(val)

        except ValueError as e:
            assert False, "Test: '{0}'. Incorrect parameter: {1}. URL: {2}.".format(test_info["title"], str(e), self.query)

        # If skip_file_check not declared, default to False:
        if "skip_file_check" not in mutatable_dict:
            mutatable_dict["skip_file_check"] = False
        test_info = mutatable_dict
        # Make each possible value line up with what the files returns:
        test_info = self.renameKeysToStandard(test_info)
        return test_info

    def renameKeysToStandard(self, json_dict):
        ### processingLevel:
        for key in ["Processing Level", "processingLevel"]:
            if key in json_dict:
                json_dict["processinglevel"] = json_dict.pop(key)
        return json_dict


