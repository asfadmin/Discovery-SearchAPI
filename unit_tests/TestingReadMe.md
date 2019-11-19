#PyTest ReadMe: A 'quick' guide

(follow readme in root of project on setting up environment first)

## How to Run Tests:
(paths assume you're in root of project, but should work from anywhere)
```bash
pytest <pytest args> test_mainManager.py <custom args>
```

   + Most common **pytest args**:
        (-v | -vv | -vvv): Print more information, with -vvv being the most
        -s: If python has print statements, this lets you see them.
        -x: Quit as soon as the first test fails
        -rs: (by itself) Print *why* each test was skipped to screen.
        -n INT: (by itself) Number of tests to run at once. (Default = 1, USE THIS!!)

   + All **Custom args**:
        --api [DEV|TEST|PROD]: Run against that api. If value doesn't match
                    these three options, it assumes the value IS the url to use.
        --only-run <SomeTitle>: Only run tests that contain this string.
        --dont-run <SomeTitle>: Dont run tests that contain this string.
        --only-run-file <File>: Only run yamls that contain this in their name.
        --dont-run-file <File>: Dont run yamls that contain this in their name.

## Writting Tests Notes:
The suite will automatically figure out which test is which, based on the 
parameters, **except** for URL tests. Since there's no 'required' params for 
those, you need to have 'url tests' at the top of the yaml list, instead of 
'tests'.

For yaml tests, they need to be in the following format:

```yaml
api: DEV
tests:      (<- or 'url tests' if testing urls)
- title of test 1:
    param1: asdf
    param2:
        - asdf1
        - asdf2
- title of test 2:
    param3: null
```

#### All Yaml Tests:
   + Custom Global Tags at top of Yaml:
    (These get overridden if the custom arguments are used in command)
        'api: [DEV|TEST|PROD]' => set default api for all tests in file.
        (More coming soon...)

   + Custom Tags available inside *each* test:
        'print: [True|False]' => print information on that specific test. 
        (Defaults to True *IF* you don't assert anything).

#### APIUtils/FilesToWKT Test Params:
   + 'test wkt': (Required) The string WKT, *or* path to file to file to 
                test. Can be a list of wkt's/files
   + 'parsed wkt': If 'test wkt' is a file, verify it's output is equal to this.
   + 'repaired wkt': Sets both 'repair wkt wrapped' and 'repair wkt unwrapped' 
                if they aren't declared.
   + 'repaired wkt wrapped/unwrapped': verify APIUtils/repairWKT's output 
                is equal to this. (For positive test cases).
   + 'repair': Checks repairs of wkt AND num of repairs against this. Can 
                be list of repairs. defaults to empty list if 'test wkt' 
                is used. Use 'check repair: False' to override this.
   + 'repaired error msg': Asserts repairing WKT returns an error 
                containing this msg.
   + 'parsed error msg': Asserts parsing file returns an error containing 
                this msg.

#### URLs Test Params:
   + 'expected file': Expected type of file returned by API. (json, csv, etc.)
   + 'expected code': Http code returned by API. (200, 400, 404, etc.)
    Note: All unknown keywords are assumed to be apart of the url.
        Keywords get joined as key=value, and added to the end of the api query.

#### CMR Input Test Params:
   + 'parser': (Required) Which parser to use. All *single* param parsers 
                in CMR/Input.py are added.
   + 'input': (Required) Input to send through the parser
   + 'expected': What you expect to return. (very literal, you 
                can have lists in lists).
   + 'expected error': Asserts the error message thrown contains this msg.

