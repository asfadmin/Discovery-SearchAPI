## Writting tests for SearchAPI:
(Docs for the manager that runs these tests: https://github.com/asfadmin/Discovery-PytestAutomation)

### Yml Keys for RepairWKT:
  ---- Input options:
	* "test wkt": (Required) The wkt you want to test.
	* print: (Default True, unless an assert key is used). Prints info on test as it's running.
	* "check repair": (Default false, unless 'repaired wkt' is used) If you have a wkt that needs repairing, but don't care what is repaired, this will override the check.
  ---- Assert Pass/Fail options:
	* "repaired wkt": How you expect the wkt to look after  it's repaired.
	* "errors": You expect the test to error out with this mesasge, instead of returning a wkt.
	* repair: (Default emtpy list) The repair(s) you expect to happen to the wkt. (Verifies the message is in the repair output)

### Yml Keys for FilesToWKT:
  ---- Input options:
	* "file wkt": (Required) The path to which file to load. Starts after 'yml_tests/Resources/'
	* "print": (Default True, unless assert statement is used). Prints info on test as it's running.
	* "check errors": (Default False, unless assert statement is used). If you need to check errors returned by API.
  ---- Assert Pass/Fail options:
	* "parsed wkt": The wkt you expect to come from the file.
	* "errors": (Default emtpy list) The error you expect the file to throw.
		(Note: If you have a zip, with one good and bad file, the api should return BOTH "parsed wkt" and "errors").

### Yml Keys for URLs (SearchAPI end-to-end tests):
##### (Note: This suite doesn't have any required keys. Any test that doesn't match any of the other test-types, will assume to be for this one.)
  ---- Input options:
  	* "print": (Default True, unless assert statement is used). Prints info on test as it's running.
  	* "skip_file_check": (Default False) Overrides checking contents of file.
  ---- Assert Pass/Fail options:
  	* "expected file": The type of file you expect the API to return. ("error json" for bad request).
  	* "expected code": Http return code expected from request.
  ---- Other Keys:
  	If key is not in the above list, it will be added to url sent to API as "https://url.com/?key1=val1,key2=val2..." etc.
  	The test suite automatically checks if the file contains the expected key, if it's a key/file pair it knows how to check for.
  	Current known files: json, jsonlite, download, csv, count
  	Current known keys: Platform, absoluteOrbit, asfframe, granule_list, groupid, flightdirection, offnadirangle, polarization, relativeorbit, collectionname, beammode, processinglevel, flightline, lookdirection, start, end, season