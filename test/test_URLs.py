
import os, yaml, pytest
import hashlib
import requests


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
            # Take out all of the timestamp stuff, hash the rest and see if it's the same as the empty hash:
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


# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the parametrize:
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
yaml_name = os.path.splitext(os.path.basename(__file__))[0]+".yml"
yaml_path = os.path.join(project_root, "test", yaml_name)

if not os.path.exists(yaml_path):
    print("File not Found: " + yaml_path)
    exit(1)
with open(yaml_path, "r") as yaml_file:
    try:
        yaml_dict = yaml.safe_load(yaml_file)
        api_keyword = yaml_dict['API']
        list_of_tests = yaml_dict["tests"]
    except yaml.YAMLError as e:
        print("###########")
        print("Failed to parse yaml: {0}".format(str(e)))
        print("###########")
        exit(2)
    except KeyError as e:
        print("###########")
        print("Failed to find key in Yaml: {0}".format(str(e)))
        print("###########")
        exit(3)

# Figure out which API to use:
if api_keyword.upper() == "TEST":
    api_url = "https://api-test.asf.alaska.edu/services/search/param?"
elif api_keyword.upper() == "PROD":
    api_url = "https://api.daac.asf.alaska.edu/services/search/param?"
elif api_keyword.upper() == "LOCAL": # Not yet tested. May need "services/search..." part
    api_url = "http://127.0.0.1:5000/"
else:
    api_url = api_keyword

@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachURLInYaml(json_test):
    title = list(json_test.keys())[0]
    json_test = next(iter(json_test.values()))
    json_test["title"] = title
    RunSingleURLFromFile(json_test, api_url)