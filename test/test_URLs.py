
import os, yaml
import pytest, warnings
import hashlib
import requests
import glob
import itertools
import argparse
import conftest

class RunSingleURLFromFile():
    def __init__(self, json_dict, url_api):
        # DONT add these to url. (Used for tester). Add ALL others to allow testing keywords that don't exist
        reserved_keys = ["expected file","expected code", "title"]
        keywords = []
        for key,val in json_dict.items():
            # If it's reserved, move on:
            if key in reserved_keys:
                continue
            # IF val is None, just add the key. Else add "key=val"
            if val == "None":
                keywords.append(str(key))
            # If you're testing multiple SAME params, add each key-val pair:
            elif isinstance(val, type([])):
                for sub_val in val:
                    if sub_val == "None":
                        keywords.append(str(key))
                    else:
                        keywords.append(str(key)+"="+str(sub_val))
            else:
                keywords.append(str(key)+"="+str(val))
        self.query = url_api + "&".join(keywords)
        status_code, returned_file = self.runQuery()

        if "expected code" in json_dict:
            assert json_dict["expected code"] == status_code, "Status codes is different than expected. Test: {0}".format(json_dict["title"])
        if "expected file" in json_dict:
            assert json_dict["expected file"] == returned_file, "Different file type returned than expected. Test: {0}".format(json_dict["title"])

        if "expected file" not in json_dict and "expected code" not in json_dict:
            print()
            print("URL: {0}".format(self.query))
            print("Status Code: {0}. File returned: {1}".format(status_code, returned_file))
            print()


    def runQuery(self):
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
            blank_csv = '"Granule Name","Platform","Sensor","Beam Mode","Beam Mode Description","Orbit","Path Number","Frame Number","Acquisition Date","Processing Date","Processing Level","Start Time","End Time","Center Lat","Center Lon","Near Start Lat","Near Start Lon","Far Start Lat","Far Start Lon","Near End Lat","Near End Lon","Far End Lat","Far End Lon","Faraday Rotation","Ascending or Descending?","URL","Size (MB)","Off Nadir Angle","Stack Size","Baseline Perp.","Doppler","GroupID"\n'
            if file_content == blank_csv:
                content_type = "blank csv"
        ## DOWNLOAD / PLAIN
        elif content_type == "plain":
            content_type = "download"
            # Take out all of the timestamp stuff, then hash the rest and see if it's the same as the empty hash:
            file_content = file_content[927:]
            # If the hash is equal to the empty-download-script hash:
            if hashlib.md5(file_content.encode()).hexdigest() == "3e4671accc22375e305bb8c6e5b61d57":
                content_type = "empty download"

        ## GEOJSON
        elif content_type == "geojson":
            if file_content == '{\n  "features": [],\n  "type": "FeatureCollection"\n}':
                content_type = "empty geojson"
        ## JSON
        elif content_type == "json":
            if "error" in file_content:
                content_type = "error json"
            elif file_content == '[\n  []\n]':
                content_type = "blank json"
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

        return h.status_code, content_type

def getTestsFromDirectory(dir_path):
    list_of_tests = []
    for file in glob.glob(dir_path, recursive=True):
        with open(file, "r") as yaml_file:
            try:
                yaml_dict = yaml.safe_load(yaml_file)
                api = yaml_dict["API"] if "API" in yaml_dict else None
                if "tests" in yaml_dict:
                    # pair the test with what api the test is expected to use:
                    tests = zip(yaml_dict["tests"], itertools.repeat(api))
                    list_of_tests.extend(tests)
                yaml_file.close()
            except yaml.YAMLError as e:
                print("###########")
                print("Failed to parse yaml: {0}".format(str(e)))
                print("###########")
                continue
    return list_of_tests




# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the @pytest.mark.parametrize:
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
list_of_tests = []

# Get the tests from all *yml* files:
tests_root = os.path.join(project_root, "test","**","test_*.yml")
print(tests_root)
list_of_tests.extend(getTestsFromDirectory(tests_root))
# Same, but with *yaml* files now:
tests_root = os.path.join(project_root, "test","**","test_*.yaml")
list_of_tests.extend(getTestsFromDirectory(tests_root))


@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachURLInYaml(json_test, api, only_run):
    # api = commandline override, --api
    # only_run = commandline only run tests that begin with, --only-run
    test_info = json_test[0]
    title = list(test_info.keys())[0]
    test_info = next(iter(test_info.values()))
    test_info["title"] = title

    # If they passed '--only-run val', and val not in test title:
    if only_run != None and only_run not in test_info["title"]:
        pytest.skip("Title of test did not match --only-run param")
    api_url = api if api != None else json_test[1]
    if api_url == None or api_url.upper() == "TEST":
        if api_url == None:
            warnings.warn(UserWarning("API not declared (DEV/TEST). Defaulting to Test."))
        api_url = "https://api-test.asf.alaska.edu/services/search/param?"
    elif api_url.upper() == "PROD":
        api_url = "https://api.daac.asf.alaska.edu/services/search/param?"

    RunSingleURLFromFile(test_info, api_url)