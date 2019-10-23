# A Quick How-To for writing tests in the url-checker

How to run tests:
	1) cd to project root.
	2) pytest <args> test/
			possible args:
				(-v | -vv | -vvv): Print more information, with -vvv being the most
				-s: If python has print statements, this lets you see them.
				-x: Quit as soon as the first test fails

How to switch the API:
	> Right now it's set at the top of the yml file. You can either pass "DEV" or "PROD",
		and it will use the corresponding url.

How to write tests:
	> Except for "expected file" and "expected code", every variable is assumed to be
		a parameter for the url. This way, "asdf: asdf" can be added like:
			"param?platform=SA&asdf=asdf". 
		Note, to JUST send asdf, do "asdf: None" for:
			"param?platform=SA&asdf"
	> If Neither of the exceptions are used, it will print the result to 
		the console instead.
	> For "expected file": Every valid "output" has the same expected type, along with
		a "blank" variant. "blank kml", "blank count", etc. (blank count is just 0).
		There is also a "error json" type, that gets returned mainly with 400 errors.


EXAMPLES:
	(These all *should* pass)
	##########################
	Expects the correct file, along with 200:
	- test full pass:
    	polarization: HH
    	platform: SA
    	maxresults: 10
    	output: csv

    	expected file: csv
    	expected code: 200
   	##########################
   	Bad beamMode param means you'll get a blank kml:
   	- test partial pass:
    	beamMode: Test
    	output: KML

    	expected file: blank kml
    	expected code: 200
   	##########################
   	If JUST bad output, get default VALID metalink:
	- test returns different file:
	    output: asdf
	    platform: SA
	    polarization: HH
	    maxresults: 10

	    expected file: metalink
	    expected code: 200
	##########################
	If NOT valid query, get "error json" file with 400:
	- test complete fail:
	    output: csv
	    maxresults: 10

	    expected file: error json
	    expected code: 400
	##########################



TODO: ADD way to run tests in different yamls. Need list of 
			test yamls stored somewhere. (another yaml?)
	  ADD way to override ALL api (dev/prod) at once, for prod releases. put in CLI?