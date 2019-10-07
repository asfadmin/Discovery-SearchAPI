#!/bin/bash
clear
LOG_LOCATION=/path/to/my/location/
exec > >(tee -i $LOG_LOCATION/apitest.log)
exec 2>&1
echo "Starting wget search test cases from api-test.asf.alaska.edu. Log Location should be: [ $LOG_LOCATION]"

# queries designed just for testing
# absoluteOrbit Keyword
wget -d -O API-TEST-absoluteOrbit-single-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?absoluteorbit=5000&maxresults=10&output=csv"
wget -d -O API-TEST-absoluteOrbit-rangle-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?absoluteorbit=5000-6000&maxresults=10&output=csv"
wget -d -O API-TEST-absoluteOrbit-list-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?absoluteorbit=5000,5001,5002&maxresults=10&output=csv"
wget -d -O API-TEST-absoluteOrbit-list-range-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?absoluteorbit=5000,5100-5200&maxresults=100&output=csv"
wget -d -O API-TEST-absoluteOrbit-list-R1-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?absoluteorbit=5000,5001,5002&platform=R1&maxresults=10&output=csv"

# asfframe Keyword
wget -d -O API-TEST-asfframe-platformR1-single-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?asfframe=345&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-asfframe-platformR1-list-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?asfframe=345,346,347&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-asfframe-platformR1-range-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?asfframe=345-347&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-asfframe-platformR1-list-range-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?asfframe=340,345-347&platform=R1&maxresults=10&output=csv"

# bbox Keyword
wget -d -O API-TEST-bbox-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5&maxresults=10&output=csv"

# beamMode Keyword
wget -d -O API-TEST-beamMode-list-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamMode=FBD,FBS,Standard&maxresults=100&output=csv"
wget -d -O API-TEST-beamMode-Standard-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamMode=Standard&maxresults=10&output=csv"
wget -d -O API-TEST-beamMode-list-R1-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamMode=Standard,STD,Fine,High,Low,Wide,Narrow,ScanSAR+Wide,ScanSAR+Narrow&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-TEST-beamMode-list-S1-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamMode=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1A&maxresults=100&output=csv"
wget -d -O API-TEST-beamMode-list-SB-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamMode=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1B&maxresults=100&output=csv"
wget -d -O API-TEST-beamMode-POL-RPI-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamMode=POL,RPI&maxresults=100&output=csv"


# beamSwath Keyword
wget -d -O API-TEST-beamSwath-1-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=1&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-Airsar-list-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=3FP,ATI,XTI&platform=AIRSAR&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-list-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=FN1,FN2,FN3,FN4,FN5&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-STD-ERS1-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=STD&platform=ERS-1&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-STD-ERS2-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=STD&platform=ERS-2&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-STD-JERS-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=STD&platform=JERS-1&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-STD-SS-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=STD&platform=SEASAT&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-ALOS-list-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=1,2,3,4,5,6,7,8,9,10,11,12,15,16,17,18,19,20&platform=ALOS&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-R1-list-S-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=SNA,SNB,ST1,ST2,ST3,ST4,ST5,ST6,ST7&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-R1-SW-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=SWA,SWB&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-R1-list-WD-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=WD1,WD2,WD3&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-R1-list-E-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=EH3,EH4,EH6,EL1&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-SA-list-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1A&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-SB-list-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1B&maxresults=100&output=csv"
wget -d -O API-TEST-beamSwath-UA-list-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?beamSwath=UAVSAR&platform=POL,RPI&maxresults=100&output=csv"

# collectionName Keyword
wget -d -O API-TEST-colName-Haiti-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?collectionName=Haiti&maxresults=100&output=csv"
wget -d -O API-TEST-colName-Iceland-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?collectionName=Iceland&maxresults=100&output=csv"
wget -d -O API-TEST-colName-earthquake-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?collectionName=earthquake&maxresults=100&output=csv"
wget -d -O API-TEST-colName-AIRSAR-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?collectionName=AIRSAR&maxresults=100&output=csv"
wget -d -O API-TEST-colName-Denali-100-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?collectionName=Denali&maxresults=100&output=csv"

# end Keyword
wget -d -O API-TEST-end-count-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?end=2005-01-01T00:00:00Z&output=count"
wget -d -O API-TEST-end-now-count-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?end=now&output=count"

# flightDirection Keyword
wget -d -O API-TEST-flightDir-A-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=A&maxresults=10&output=csv"
wget -d -O API-TEST-flightDir-ASC-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=ASC&maxresults=10&output=csv"
wget -d -O API-TEST-flightDir-ASCENDING-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=ASCENDING&maxresults=10&output=csv"
wget -d -O API-TEST-flightDir-D-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=D&maxresults=10&output=csv"
wget -d -O API-TEST-flightDir-DES-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=DESC&maxresults=10&output=csv"
wget -d -O API-TEST-flightDir-DESCENDING-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=DESCENDING&maxresults=10&output=csv"
wget -d -O API-TEST-flightDir-asCEndInG-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=asCEndInG&maxresults=10&output=csv"
wget -d -O API-TEST-flightDir-dEsCeNding-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightDirection=dEsCeNding&maxresults=10&output=csv"

# flightLine Keyword
wget -d -O API-TEST-flightLine-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightLine=15302&maxresults=10&output=csv"
wget -d -O API-TEST-flightLine-gilmorecreek-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?flightLine=gilmorecreek045-1.93044&maxresults=10&output=csv"

# frame Keyword
wget -d -O API-TEST-frame-single-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?frame=345&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-frame-range-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?frame=345-347&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-frame-list-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?frame=345,346,347&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-frame-list-range-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?frame=340,345-347&platform=R1&maxresults=10&output=csv"

# granule_list Keyword
wget -d -O API-TEST-granule_list-single-csv-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=csv"
wget -d -O API-TEST-granule_list-single-count-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=count"
wget -d -O API-TEST-granule_list-single-metalink-valid.metalink "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=metalink"
wget -d -O API-TEST-granule_list-single-kml-valid.kml "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=kml"
wget -d -O API-TEST-granule_list-single-json-valid.json "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=json"
wget -d -O API-TEST-granule_list-single-geo-json-valid.geo.json "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=geo.json"
wget -d -O API-TEST-granule_list-single-download-valid.py "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=download"
wget -d -O API-TEST-granule_list-single-map-valid.map "https://api-test.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=map"

# groupid Keyword
wget -d -O API-TEST-groupid-number-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=12345&output=json"
wget -d -O API-TEST-groupid-hash-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=sdfkhgsdfkhgsdf&output=json"
wget -d -O API-TEST-groupid-sentinel-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=S1A_IWDV_0382_0387_019686_014&output=json"
wget -d -O API-TEST-groupid-s1-insar-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=S1-GUNW-D-R-087-tops-20190816_20190804-161614-19149N_17138N-PP-fee7-v2_0_2&output=json"
wget -d -O API-TEST-groupid-smap-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=SP_15077_D_005&output=json"
wget -d -O API-TEST-groupid-uavsar-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=UA_EcuVol_17700_15024_006_150319_L090_CX_01&output=json"
wget -d -O API-TEST-groupid-alos-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=ALPSRP278477070&output=json"
wget -d -O API-TEST-groupid-airsar-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=ts1902&output=json"
wget -d -O API-TEST-groupid-radarsat-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=R1_63781_FN1_F277&output=json"
wget -d -O API-TEST-groupid-ers-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=E1_08794_STD_F267&output=json"
wget -d -O API-TEST-groupid-jers-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=J1_01508_STD_F315&output=json"
wget -d -O API-TEST-groupid-seasat-valid.json "https://api-test.asf.alaska.edu/services/search/param?groupid=SS_01499_STD_F1200&output=json"

# intersectswith Keyword
wget -d -O API-TEST-intersectsWith-point-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=point%28-119.543+37.925%29&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-polygon-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=polygon%28%28-119.543 37.925+ -118.443 37.7421+ -118.682 36.8525+ -119.77 37.0352+ -119.543 37.925%29%29&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-linestring-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=linestring(-119.543 37.925, -118.443 37.7421)&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-point-1000-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=point(-119.543 37.925)&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-polygon-10000-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=polygon((-119.543 37.925, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925))&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-polygon2-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=polygon(-119.543 37.925, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925)&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-linestring-invalid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=linestring(TEST)&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-linestring2-invalid.CSV "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=linestring(%)&maxResults=1000&output=CSV"

# linestring Keyword
wget -d -O API-TEST-linestring-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?linestring=-150.2,65.0,-150.1,65.5&maxresults=10&output=csv"

# lookDirection Keyword
wget -d -O API-TEST-lookDir-LEFT-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?lookDirection=LEFT&maxresults=10&output=csv"
wget -d -O API-TEST-lookDir-RIGHT-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?lookDirection=RIGHT&maxresults=10&output=csv"
wget -d -O API-TEST-lookDir-L-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?lookDirection=L&maxresults=10&output=csv"
wget -d -O API-TEST-lookDir-R-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?lookDirection=R&maxresults=10&output=csv"

# maxBaselinePerp Keyword
wget -d -O API-TEST-maxBaselinePerp-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?maxbaselineperp=150&platform=R1&maxresults=10&output=csv"

# maxDoppler Keyword
wget -d -O API-TEST-maxDoppler-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?maxdoppler=2000&platform=R1&maxresults=10&output=csv"

# maxFaradayRotation Keyword
wget -d -O API-TEST-maxFaradayRotation-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?maxfaradayrotation=3&maxresults=10&output=csv"

# maxInsarStackSize Keyword
wget -d -O API-TEST-maxInsarStackSize-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?maxinsarstacksize=50&maxresults=10&output=csv"

# maxResults Keyword
wget -d -O API-TEST-maxResults-1-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=csv"
wget -d -O API-TEST-maxResults-1-valid.json "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=json"
wget -d -O API-TEST-maxResults-1-valid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=jsonlite"
wget -d -O API-TEST-maxResults-1-valid.geojson "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=geojson"
wget -d -O API-TEST-maxResults-2-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=csv"
wget -d -O API-TEST-maxResults-2-valid.json "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=json"
wget -d -O API-TEST-maxResults-1-valid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=jsonlite"
wget -d -O API-TEST-maxResults-2-valid.geojson "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=geojson"

# minBaselinPerp Keyword
wget -d -O API-TEST-minBaselinePerp-150-10-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?minbaselineperp=150&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-minBaselinPerp-100-150-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?minbaselineperp=100&maxbaselineperp=150&platform=R1&maxresults=10&output=csv"

# minDoppler Keyword
wget -d -O API-TEST-minDoppler1-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?mindoppler=-20000&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-minDoppler2-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?mindoppler=-2000&maxdoppler=2000&platform=R1&maxresults=10&output=csv"

# minFaradayRotation Keyword
wget -d -O API-TEST-minFaradayRot-3-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?minfaradayrotation=3&maxresults=10&output=csv"
wget -d -O API-TEST-minFaradayRot-2-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?minfaradayrotation=2&maxfaradayrotation=3&maxresults=10&output=csv"

# minInsarStackSize Keyword
wget -d -O API-TEST-minInsarStackSize-50-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?mininsarstacksize=50&maxresults=10&output=csv"
wget -d -O API-TEST-minInsarStackSize-80-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?mininsarstacksize=80&maxinsarstacksize=100&maxresults=10&output=csv"

#  offNadirAngle Keyword
wget -d -O API-TEST-offNadirAngle-single-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?offnadirangle=21.5&maxresults=10&output=csv"
wget -d -O API-TEST-offNadirAngle-list-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?offnadirangle=21.5,23.1,27.1&maxresults=10&output=csv"
wget -d -O API-TEST-offNadirAngle-range-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?offnadirangle=20-30&maxresults=10&output=csv"

# output keyword
wget -d -O API-TEST-platform-SB-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=csv"
wget -d -O API-TEST-platform-SB-count-valid.CSV "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=count"
wget -d -O API-TEST-platform-SB-download-valid.py "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=download"
wget -d -O API-TEST-platform-SB-geojson-valid.geojson "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=geojson"
wget -d -O API-TEST-platform-SB-json-valid.json "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=json"
wget -d -O API-TEST-platform-SB-jsonlite-valid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=jsonlite"
wget -d -O API-TEST-platform-SB-kml-valid.kml "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=kml"
wget -d -O API-TEST-platform-SB-metalink-valid.metalink "https://api-test.asf.alaska.edu/services/search/param?platform=SB&maxresults=2000&output=metalink"

# platform Keyword
wget -d -O API-TEST-platform-SA-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SA&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"
wget -d -O API-TEST-platform-SB-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=csv"
wget -d -O API-TEST-platform-J1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=J1&polygon=-148.52,64.63,-150.41,64.64,-149.58,63.86,-148.52,64.63&maxResults=100&output=csv"
wget -d -O API-TEST-platform-A3-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=A3&processinglevel=L1.0polygon=-148.52,64.63,-150.41,64.64,-149.58,63.86,-148.52,64.63&maxResults=100&output=csv"
wget -d -O API-TEST-platform-Sentinel-1A-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel-1A&maxResults=10&output=csV"
wget -d -O API-TEST-platform-R1-E1-valid.json "https://api-test.asf.alaska.edu/services/search/param?platform=R1,E1&maxResults=10&output=jSoN"
wget -d -O API-TEST-platform-R1-E1-10-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=RADARSAT-1,E1&maxResults=10&output=csv"
wget -d -O API-TEST-platform-R1-E1-L0-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=RADARSAT-1,E1&processingLEVEL=L0,L1&maxResults=10&output=csv"
wget -d -O API-TEST-platform-SP-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SP&maxResults=10&output=csv"
wget -d -O API-TEST-platform-UA-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UA&maxResults=10&output=csv"
wget -d -O API-TEST-platform-E1E2-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=E1,E2&maxResults=10&output=csv"
wget -d -O API-TEST-platform-SIRC-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SIR-C&maxResults=10&output=csv"
wget -d -O API-TEST-platform-SIRC-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=STS-59&maxResults=10&output=csv"
wget -d -O API-TEST-platform-SIRC-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=STS&maxResults=10&output=csv"
wget -d -O API-TEST-platform-SIRC-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=STS-68,STS-59&maxResults=10&output=csv"

# platform aliases + count output
wget -d -O API-TEST-platform-S1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=S1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SENTINEL1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Sentinel-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-s1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=s1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-ERS-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ERS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-erS-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=erS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-R1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=R1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-r1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=r1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-RADARSAT-1-count-0results-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=RADARSAT-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Radarsat-1-count-0results-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Radarsat-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-E1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=E1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-ERS-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ERS-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Ers-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Ers-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-E2-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=E2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-ERS-2-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ERS-2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-e2-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=e2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-ers-2-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ers-2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-J1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=J1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-JERS-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=JERS-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Jers-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Jers-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-j1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=j1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-A3-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=A3&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-ALOS-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ALOS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-a3-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=a3&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-alos-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=alos&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Alos-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Alos&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-AS-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=AS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-DC8-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=DC-8&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-AIRSAR-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=AIRSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Airsar-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Airsar&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-as-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=as&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-AiRSAR-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=AiRSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-dc-8-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=dc-8&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SS-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SEASAT-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SEASAT%201&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SEASAT-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SEASAT&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-ss-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ss&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Seasat-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Seasat&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SeaSAT-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SeaSAT%201&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SA-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SA&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Sentinel-1A-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel-1A&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-sa-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=sa&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-sentinel-1a-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=sentinel-1a&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SENTINEL-1A-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1A&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Sb-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sb&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SB-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SB&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Sentinel-1B-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel-1B&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SB-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1B&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SP-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SP&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Sp-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sp&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-sp-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=sp&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-SMAP-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SMAP&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Smap-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Smap&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-smap-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=smap&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-UA-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UA&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-ua-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ua&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-Ua-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Ua&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-UAVSAR-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAVSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-UAvSAR-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAvSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-G-III-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=G-III&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-g-iii-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=g-iii&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-TEST-platform-STS-59-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=STS-59&output=count"
wget -d -O API-TEST-platform-STS-68-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=STS-68&output=count"
wget -d -O API-TEST-platform-STS-59-68-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=STS-59,STS-68&output=count"
wget -d -O API-TEST-platform-sts-59-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=sts-59&output=count"
wget -d -O API-TEST-platform-StS-68-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=StS-68&output=count"
wget -d -O API-TEST-platform-Sts-59-StS-68-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sts-59,StS-68&output=count"

# point Keyword
wget -d -O API-TEST-point-valid.csv "https://api-test.asf.alaska.edu/services/search/param?point=-150.2,65.0&maxresults=10&output=csv"

# polarization Keyword
wget -d -O API-TEST-polar-HH-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=HH&platform=SA&maxresults=10&output=csv"
wget -d -O API-TEST-polar-VV-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=VV&platform=SA&maxresults=10&output=csv"
wget -d -O API-TEST-polar-HH-HV-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=HH%2bHV&maxresults=10&output=csv"
wget -d -O API-TEST-polar-DualVV-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Dual+VV&maxresults=10&output=csv"
wget -d -O API-TEST-polar-QUADRATURE-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=QUADRATURE&maxresults=10&output=csv"
wget -d -O API-TEST-polar-VV-VH-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=VV%2bVH&maxresults=10&output=csv"
wget -d -O API-TEST-polar-DualHV-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Dual+HV&maxresults=10&output=csv"
wget -d -O API-TEST-polar-DualVH-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Dual+VH&maxresults=10&output=csv"
wget -d -O API-TEST-polar-DualVH-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Dual+VH&maxresults=10&output=csv"
wget -d -O API-TEST-polar-hH-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=hH&platform=SA&maxresults=10&output=csv"
wget -d -O API-TEST-polar-Vv-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Vv&platform=SA&maxresults=10&output=csv"
wget -d -O API-TEST-polar-Hh-hV-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Hh%2bhV&maxresults=10&output=csv"
wget -d -O API-TEST-polar-Dualvv-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Dual+vv&maxresults=10&output=csv"
wget -d -O API-TEST-polar-quadrature-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=quadrature&maxresults=10&output=csv"
wget -d -O API-TEST-polar-vv-VH-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=vv%2bVH&maxresults=10&output=csv"
wget -d -O API-TEST-polar-Dualhv-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=Dual+hv&maxresults=10&output=csv"
wget -d -O API-TEST-polar-dualVH-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=dual+VH&maxresults=10&output=csv"
wget -d -O API-TEST-polar-dualvh-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polarization=dual+vh&maxresults=10&output=csv"

# polygon Keyword
wget -d -O API-TEST-polygon-multi-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=12.13,41.74,13.4,41.74,13.4,42.75,12.13,42.75,12.13,41.74&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"
wget -d -O API-TEST-polygon-4-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=-148.52,64.63,-150.41,64.64,-149.58,63.86,-148.52,64.63&maxResults=100&output=csv"

# processingLevel Keyword
wget -d -O API-TEST-procLevel-L11-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=L1.1&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-L11-L1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=L1.1,L1.0&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-list-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=3FP,ATI,LTIF,PTIF,CTIF,PSTOKES,BROWSE,DEM,CSTOKES,JPG,LSTOKES,THUMBNAIL&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-RTC-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=RTC_LOW_RES,RTC_HI_RES&platform=ALOS&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-ERS-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=L0,L1,BROWSE,THUMBNAIL&platform=ERS-1,ERS-2&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-JERS1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=L0,L1,BROWSE,THUMBNAIL&platform=JERS-1&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-R1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=L0,L1,BROWSE,THUMBNAIL&platform=RADARSAT-1&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-SS-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=L1,BROWSE,THUMBNAIL&platform=SEASAT&maxResults=10&output=CSV"
wget -d -O API-TEST-procLevel-S1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=METADATA_GRD,GRD_HS,GRD_HD,GRD_MS,GRD_MD,GRD_FS,GRD_FD,SLC,RAW,OCN,METADATA_RAW,METADATA,METADATA_SLC, THUMBNAIL&platform=Sentinel-1A,Sentinel-1B&maxResults=100&output=CSV"
wget -d -O API-TEST-procLevel-SMAP-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=L1A_Radar_RO_QA,L1B_S0_LoRes_HDF5,L1B_S0_LoRes_QA,L1B_S0_LoRes_ISO_XML,L1A_Radar_QA,L1A_Radar_RO_ISO_XML, L1C_S0_HiRes_ISO_XML,L1C_S0_HiRes_QA,L1C_S0_HiRes_HDF5,L1A_Radar_HDF5&platform=SMAP&maxResults=100&output=CSV"
wget -d -O API-TEST-procLevel-UA-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=KMZ,PROJECTED,PAULI,PROJECTED_ML5X5,STOKES,AMPLITUDE,BROWSE,COMPLEX,DEM_TIFF,PROJECTED_ML3X3,METADATA,AMPLITUDE_GRD,INTERFEROMETRY,INTERFEROMETRY_GRD,THUMBNAIL&platform=UAVSAR&maxResults=100&output=CSV"


# processingDate Keyword
wget -d -O API-TEST-procDate-Z-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingDate=2018-01-01T00:00:00Z&maxresults=10&output=csv"
wget -d -O API-TEST-procDate-yesterday-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingDate=yesterday&maxresults=10&output=csv"
wget -d -O API-TEST-procDate-1weekago-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingDate=1+week+ago&maxresults=10&output=csv"
wget -d -O API-TEST-procDate-today-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingDate=today&maxresults=10&output=csv"
wget -d -O API-TEST-procDate-monthago-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingDate=month+ago&maxresults=10&output=csv"
wget -d -O API-TEST-procDate-2monthago-valid.csv "https://api-test.asf.alaska.edu/services/search/param?processingDate=2+month+ago&maxresults=10&output=csv"

# product_list Keyword
wget -d -O API-TEST-product_list-S1-valid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040550_20141003T040619_002660_002F64_EC04-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040644_20141003T040709_002660_002F64_9E20-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040709_20141003T040734_002660_002F64_4C78-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040734_20141003T040754_002660_002F64_288E-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053708_20141003T053737_002661_002F66_A2F4-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053737_20141003T053802_002661_002F66_6132-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053802_20141003T053827_002661_002F66_18D8-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053827_20141003T053852_002661_002F66_5DF0-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053852_20141003T053917_002661_002F66_C3AA-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053917_20141003T053942_002661_002F66_014F-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053942_20141003T054007_002661_002F66_7F10-GRD_HD,S1A_IW_GRDH_1SDV_20141003T054007_20141003T054032_002661_002F66_825E-GRD_HD&output=jsonlite"
wget -d -O API-TEST-product_list-mix-valid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD&product_list=ALPSRP016350310-L1.5,ALPSRP016350320-L1.5,ALPSRP016350330-L1.5,ALPSRP016350340-L1.5,ALPSRP016350350-L1.5,ALPSRP016350360-L1.5,ALPSRP016350370-L1.5,ALPSRP016350380-L1.5&output=jsonlite"
wget -d -O API-TEST-product_list-multi-valid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD&product_list=ALPSRP016350310-L1.5&product_list=E2_23229_STD_F285-L0&product_list=R1_14387_ST5_F281-L0&product_list=E1_24859_STD_F703-L0&output=jsonlite"
wget -d -O API-TEST-product_list-multi2-valid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD&product_list=E2_18061_STD_F277-L1,E2_18061_STD_F315-L1,E2_18061_STD_F259-L1,E2_18061_STD_F295-L1&output=jsonlite"

# relativeOrbit Keyword
wget -d -O API-TEST-relativeOrbit-single-valid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeorbit=20&maxresults=10&output=csv"
wget -d -O API-TEST-relativeOrbit-range-valid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeorbit=20-22&maxresults=10&output=csv"
wget -d -O API-TEST-relativeOrbit-list-valid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeorbit=20,21,22&maxresults=10&output=csv"
wget -d -O API-TEST-relativeOrbit-list-range-valid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeorbit=20,23-24&maxresults=100&output=csv"
wget -d -O API-TEST-relativeOrbit-list-R1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeorbit=20,23,25&platform=R1&maxresults=10&output=csv"

# season Keyword
wget -d -O API-TEST-season-32-90-S1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-100-S1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-175-UA-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,175&platform=UA&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-32-90-S1-start-end-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&start=2017-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-100-S1-start-end-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&start=2015-01-01T00:00:00Z&end=2018-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-175-UA-start-end-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,175&platform=UA&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-32-90-S1-2yearago-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&start=2+year+ago&end=now&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-100-S1-2yearago-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&start=2+year+ago&end=now&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-175-UA-july2018-now-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,175&platform=UA&start=2018-July-15&end=now&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-32-90-S1-july2018-now-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&start=2018-July-15&end=now&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-100-S1-1yearago-now-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&start=1+year+ago&end=now&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-1-100-UA-3yearago-now-valid.csv "https://api-test.asf.alaska.edu/services/search/param?season=1,175&platform=UA&start=3+year+ago&end=now&maxresults=1000&output=CSV"

# start Keyword
wget -d -O API-TEST-start-Zdate-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=2005-01-01T00:00:00Z&output=count"
wget -d -O API-TEST-start-Zdate-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=2005-01-01T00:00:00Z&end=2005-01-01T01:00:00Z&output=csv"
wget -d -O API-TEST-start-3monthagoplus1day-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=3+months+and+a+day+ago&output=count"
wget -d -O API-TEST-start-june302018-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=June+30,+2018&output=count"
wget -d -O API-TEST-start-1weekago-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=1+week+ago&output=count"
wget -d -O API-TEST-start-1dayago-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=1+day+ago&output=count"
wget -d -O API-TEST-start-today-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=today&output=count"
wget -d -O API-TEST-start-yesterday-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?start=yesterday&output=count"


# new formats

# polygon closure/winding order fixer test
wget -d -O API-TEST-polygonclosure1-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=12.13,41.74,13.4,41.74,13.4,42.75,12.13,42.75&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"
wget -d -O API-TEST-polygonclosure2-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=12.13,41.74,13.4,41.74,13.4,42.75,12.13,42.75,12.13,41.74&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"
wget -d -O API-TEST-polygonclosure3-valid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=12.13,41.74,12.13,42.75,13.4,42.75,13.4,41.74,12.13,41.74&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"

# queries taken from real-world usage
wget -d -O API-TEST-realworld-1-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=point(-168.0380672+53.9279675)&platform=Sentinel-1A,Sentinel-1B&processingLevel=GRD_HS,GRD_HD&beamMode=IW&output=count"
wget -d -O API-TEST-realworld-2-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=linestring(-102+37.59,-94+37,-94+39,-102+39)&platform=Sentinel-1A,Sentinel-1B&processingLevel=GRD_HS,GRD_HD&beamMode=IW&output=count"
wget -d -O API-TEST-realworld-3-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=polygon((-102+37.59,-94+37,-94+39,-102+39,-102+37.59))&platform=Sentinel-1A,Sentinel-1B&processingLevel=GRD_HS,GRD_HD&beamMode=IW&output=count"
wget -d -O API-TEST-realworld-4-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?output=count&frame=587%2C588%2C589%2C590%2C591%2C592%2C593&processingLevel=L0%2CL1.0%2CSLC&platform=SENTINEL-1A%2CSENTINEL-1B&maxResults=1000&relativeOrbit=128"
wget -d -O API-TEST-realworld-5-count-valid.csv "https://api-test.asf.alaska.edu/services/search/param?output=count&asfframe=587%2C588%2C589%2C590%2C591%2C592%2C593&processingLevel=L0%2CL1.0%2CSLC&platform=SENTINEL-1A%2CSENTINEL-1B&maxResults=1000&relativeOrbit=128"
wget -d -O API-TEST-realworld-6-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SA,SB&relativeOrbit=128&asfframe=587-593&start=2017-06-01&end=2018-05-30&output=csv"
wget -d -O API-TEST-realworld-7-valid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SA,SB&relativeOrbit=128&frame=587-593&start=2017-06-01&end=2018-05-30&output=csv"
wget -d -O API-TEST-realworld-8-valid.csv "https://api-test.asf.alaska.edu/services/search/param?output=csv&platform=Sentinel-1A&start=2018-05-30&end=2018-05-31%22"


### Negative Tests ###
# invalid queries
wget -d -O API-TEST-invalid-query.csv "https://api-test.asf.alaska.edu/services/search/param?output=csv&maxresults=10"
wget -d -O API-TEST-missing-query.csv "https://api-test.asf.alaska.edu/services/search/param"

# absoluteOrbit Keyword Invalid
wget -d -O API-TEST-absoluteOrbit-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?absoluteorbit=TEST&maxresults=10&output=csv"
wget -d -O API-TEST-absoluteOrbit-specch-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?absoluteorbit=@&maxresults=10&output=csv"

# asfframe Keyword Invalid
wget -d -O API-TEST-asfframe-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?asfframe=TEST&maxresults=10&output=csv"
wget -d -O API-TEST-asfframe-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?asfframe=$&maxresults=10&output=csv"

# bbox Keyword Invalid
wget -d -O API-TEST-bbox-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?bbox=TEST&output=CSV"
wget -d -O API-TEST-bbox-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?bbox=$&output=CSV"
wget -d -O API-TEST-bbox-incomplete-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=CSV"
wget -d -O API-TEST-bbox-incomplete-json-invalid.json "https://api-test.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=JSON"
wget -d -O API-TEST-bbox-incomplete-jsonlite-invalid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=JSONLITE"
wget -d -O API-TEST-bbox-incomplete-geojson-invalid.geojson "https://api-test.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=GEO.JSON"
wget -d -O API-TEST-bbox-incomplete-download-invalid.py "https://api-test.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1&output=download"

# beamMode Keyword Invalid
wget -d -O API-TEST-beamMode-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?beamMode=#&output=CSV"
wget -d -O API-TEST-beamMode-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?beamMode=TEST&output=CSV"
wget -d -O API-TEST-beamMode-TEST-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?beamMode=TEST&output=CSV,COUNT"
wget -d -O API-TEST-beamMode-specchar2-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?beamMode=@&output=CSV"

# beamSwath Keyword Invalid
wget -d -O API-TEST-beamSwath-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?beamSwath=TEST&output=CSV"
wget -d -O API-TEST-beamSwath-TEST-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?beamSwath=TEST&output=CSV,COUNT"
wget -d -O API-TEST-beamSwath-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?beamSwath=@&output=CSV"

# collectionName Keyword Invalid
wget -d -O API-TEST-collectionName-A3-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ALOS&collectionName=TEST&output=CSV"
wget -d -O API-TEST-collectionName-UA-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAVSAR&collectionName=TEST&output=CSV"
wget -d -O API-TEST-collectionName-S1-ABoVE-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1A&collectionName=ABoVE&output=CSV"
wget -d -O API-TEST-collectionName-S1-Alaska-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&collectionName=Alaska&output=CSV"
wget -d -O API-TEST-collectionName-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?collectionName=$&output=CSV"

# end Keyword Invalid
wget -d -O API-TEST-end-2020Z-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?end=2020-01-01T00:00:00Z&output=count"
wget -d -O API-TEST-end-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?end=@%&output=count"

# flightDirection Keyword Invalid
wget -d -O API-TEST-flightDir-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=E1&flightDirection=TEST&beamMode=STD&maxResults=100&output=CSV"
wget -d -O API-TEST-flightDir-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=E1&flightDirection=$&beamMode=STD&maxResults=100&output=CSV"

# flightLine Keyword Invalid
wget -d -O API-TEST-flightLine-UA-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAVSAR&flightLine=TEST&output=CSV"
wget -d -O API-TEST-flightLine-AS-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=AIRSAR&flightLine=TEST&output=CSV"
wget -d -O API-TEST-flightLine-AS-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=AIRSAR&flightLine=$&output=CSV"

# frame Keyword Invalid
wget -d -O API-TEST-frame-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ALOS&frame=TEST&maxResults=100&output=CSV"
wget -d -O API-TEST-frame-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=ALOS&frame=@&maxResults=100&output=CSV"

# granule_list Keyword Invalid
wget -d -O API-TEST-granule_list-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?granule_list=TEST&output=CSV"
wget -d -O API-TEST-granule_list-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?granule_list$#@$&output=CSV"

# groupid Keyword Invalid
wget -d -O API-TEST-groupid-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?groupid=TEST&output=csv"
wget -d -O API-TEST-groupid-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?groupid=$#&output=csv"

# intersectsWith  Keyword Invalid
wget -d -O API-TEST-intersectsWith-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=linestring(TEST)&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=linestring(%)&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-point-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=point(TEST,37.925)&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-polygon-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=polygon((TEST 37.925, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925))&maxResults=1000&output=CSV"
wget -d -O API-TEST-intersectsWith-polygon-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?intersectsWith=polygon($ $, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925)&maxResults=1000&output=CSV"


# linestring Keyword Invalid
wget -d -O API-TEST-linestring-num-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?linestring=-150.2,65.0,#&maxresults=10&output=csv"
wget -d -O API-TEST-linestring-TEST-FAIL-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?linestring=TEST,FAIL&maxresults=10&output=csv"
wget -d -O API-TEST-linestring-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?linestring(TEST)&maxResults=1000&output=CSV"
wget -d -O API-TEST-linestring-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?linestring(%)&maxResults=1000&output=CSV"

# lookDirection Keyword Invalid
wget -d -O API-TEST-lookDir-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?lookDirection=TEST&maxResults=1000&output=CSV"
wget -d -O API-TEST-lookDir-1-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?lookDirection=1&maxResults=1000&output=CSV"

# maxBaselinePerp Keyword Invalid
wget -d -O API-TEST-maxBaseLinePerp-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?maxbaselineperp=%&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-maxBaseLinePerp-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?maxbaselineperp=TEST&platform=R1&maxresults=10&output=csv"

# maxDoppler Keyword Invalid
wget -d -O API-TEST-maxDoppler-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxDoppler=TEST&output=CSV"
wget -d -O API-TEST-maxDoppler-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxDoppler=@&output=CSV"

# maxFaradayRotation Keyword Invalid
wget -d -O API-TEST-maxFaradayRotation-0-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=0&output=CSV"
wget -d -O API-TEST-maxFaradayRotation-neg-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=-5.0&output=CSV"
wget -d -O API-TEST-maxFaradayRotation-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=TEST&output=CSV"
wget -d -O API-TEST-maxFaradayRotation-empty-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=&output=CSV"
wget -d -O API-TEST-maxFaradayRotation-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=***&output=CSV"

# maxInsarStackSize Keyword Invalid
wget -d -O API-TEST-maxInsarStackSize-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL&maxInsarStackSize=#&maxResults=100&output=CSV"
wget -d -O API-TEST-maxInsarStackSize-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL&maxInsarStackSize=TEST&maxResults=100&output=CSV"

# maxResults Keyword Invalid
wget -d -O API-TEST-maxResults-0-invalid.CSV "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=csv"
wget -d -O API-TEST-maxResults-0-invalid.json "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=json"
wget -d -O API-TEST-maxResults-0-invalid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=jsonlite"
wget -d -O API-TEST-maxResults-0-invalid.geojson "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=geojson"
wget -d -O API-TEST-maxResults-a-invalid.CSV "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=csv"
wget -d -O API-TEST-maxResults-a-invalid.json "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=json"
wget -d -O API-TEST-maxResults-a-invalid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=jsonlite"
wget -d -O API-TEST-maxResults-a-invalid.geojson "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=geojson"
wget -d -O API-TEST-maxResults-%-invalid.CSV "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=csv"
wget -d -O API-TEST-maxResults-%-invalid.json "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=json"
wget -d -O API-TEST-maxResults-%-invalid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=jsonlite"
wget -d -O API-TEST-maxResults-%-invalid.geojson "https://api-test.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=geojson"

# minBaselinPerp Keyword Invalid
wget -d -O API-TEST-minBaselineperp-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?minbaselineperp=TEST&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-minBaselineperp-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?minbaselineperp=%%%&platform=R1&maxresults=10&output=csv"

# minDoppler Keyword Invalid
wget -d -O API-TEST-minDoppler-negnum-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?mindoppler=-20000&platform=R1&maxresults=10&output=csv"
wget -d -O API-TEST-minDoppler-negnum2-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?mindoppler=-2000&maxdoppler=2000&platform=R1&maxresults=10&output=csv"

# minFaradayRotation Keyword Invalid
wget -d -O API-TEST-minFaradayRot-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?minfaradayrotation=#&maxresults=10&output=csv"
wget -d -O API-TEST-minFaradayRot-specchar2-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?minfaradayrotation=#&maxfaradayrotation=#&maxresults=10&output=csv"
wget -d -O API-TEST-minFaradayRot-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?minfaradayrotation=TEST&maxfaradayrotation=TEST&maxresults=10&output=csv"
wget -d -O API-TEST-minFaradayRot-0-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=0&output=CSV"
wget -d -O API-TEST-minFaradayRot-neg5-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=-5.0&output=CSV"
wget -d -O API-TEST-minFaradayRot-specchar2-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&minFaradayRotation=&output=CSV"
wget -d -O API-TEST-minFaradayRot-specchar3-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=Sentinel&minFaradayRotation=***&output=CSV"

# minInsarStackSize Keyword Invalid
wget -d -O API-TEST-minInsarStackSize-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?mininsarstacksize=$&maxresults=10&output=csv"
wget -d -O API-TEST-minmaxInsarStackSize-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?mininsarstacksize=$&maxinsarstacksize=#&maxresults=10&output=csv"
wget -d -O API-TEST-minmaxInsarStackSize-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?mininsarstacksize=TEST&maxinsarstacksize=TEST&maxresults=10&output=csv"

#  offNadirAngle Keyword Invalid
wget -d -O API-TEST-offNadirAngle-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?offNadirAngle=TEST&maxResults=1000&output=CSV"
wget -d -O API-TEST-offNadirAngle-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?offNadirAngle=$&maxResults=1000&output=CSV"

# output Keyword Invalid
wget -d -O API-TEST-output-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=05905-05906&output=TEST"
wget -d -O API-TEST-output-SCS-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=05905-05906&maxResults=1/2&output=CSC"

# pagesize Invalid + jsonlite output
wget -d -O API-TEST-pagesize-invalid.jsonlite "https://api-test.asf.alaska.edu/services/search/param?platform=R1,E1&pagesize=TEST&output=jSoNlite"

# platform Keyword Invalid
wget -d -O API-TEST-platform-specchar1-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=@&maxResults=10&output=CSV"
wget -d -O API-TEST-platform-specchar1-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=@&maxResults=10&output=COUNT"
wget -d -O API-TEST-platform-specchar2-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=~&maxResults=10&output=COUNT"
wget -d -O API-TEST-platform-specchar3-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=%&maxResults=10&output=COUNT"
wget -d -O API-TEST-platform-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=TEST&maxResults=10&output=COUNT"

# platform aliases Keyword Invalid
wget -d -O API-TEST-platform-aliases-S2-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=S2&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"
wget -d -O API-TEST-platform-aliases-SENTI-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=SENTI&start=1+week+ago&end=now&maxresults=2000&output=csv"
wget -d -O API-TEST-platform-aliases-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=TEST&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"

# platform_list Keyword Invalid
wget -d -O API-TEST-platform_list-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform_list=Test,TEST&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"
wget -d -O API-TEST-platform_list-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform_list=#,$&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"

# point Keyword Invalid
wget -d -O API-TEST-point-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?point=-150.2&maxresults=10&output=csv"
wget -d -O API-TEST-point-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?point=$#&maxresults=10&output=csv"

# polarization Keyword Invalid
wget -d -O API-TEST-polar-numb-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=AIRSAR&polarization=12&output=CSV"
wget -d -O API-TEST-polar-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=AIRSAR&polarization=%@#&output=CSV"
wget -d -O API-TEST-polar-E1-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=E1&polarization=^*&maxResults=1000&output=CSV"

# polygon Keyword Invalid
wget -d -O API-TEST-polygon-broken-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=-155.08,65.82,-153.5,61.91,-149.50,63.07,-149.94,64.55&maxResults=1000&output=CSV"
wget -d -O API-TEST-polygon-3points-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=-155.08,65.82,-153.5&maxResults=1000&output=CSV"
pwget -d -O API-TEST-polygon-1point-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?olygon=-155.08,65.82&maxResults=1000&output=CSV"
wget -d -O API-TEST-polygon-1point-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=-155.08,65.82&maxResults=1000&output=count"
wget -d -O API-TEST-polygon-specchar-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=$$&maxResults=1000&output=count"
wget -d -O API-TEST-polygon-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=$$&maxResults=1000&output=CSV"
wget -d -O API-TEST-polygon-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=TEST&maxResults=1000&output=CSV"


# processingLevel Keyword Invalid
wget -d -O API-TEST-procLevel-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=@@&maxResults=1000&output=CSV"
wget -d -O API-TEST-procLevel-LSTOKETS-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?processingLevel=LSTOKETS&&output=COUNT"

# processingDate Keyword Invalid
wget -d -O API-TEST-procDate-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?processingDate=$$$&maxResults=1200&output=CSV"

# product_list Invalid + CSV output
wget -d -O API-TEST-product_list-numb-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?product_list=0,1,2,3,4&output=CSV"
wget -d -O API-TEST-product_list-alpha-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?product_list=a,b,c,d&output=CSV"
wget -d -O API-TEST-product_list-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?product_list=#,$,%,@&output=CSV"
wget -d -O API-TEST-product_list-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?product_list=TEST,INVALID&output=CSV"

# relativeOrbit Keyword Invalid
wget -d -O API-TEST-relativeOrbit-671-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeOrbit=671&output=CSV"
wget -d -O API-TEST-relativeOrbit-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeOrbit=TEST&output=CSV"
wget -d -O API-TEST-relativeOrbit-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?relativeOrbit=@@&output=CSV"
wget -d -O API-TEST-relativeOrbit-UA-TEST-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=TEST&output=CSV"
wget -d -O API-TEST-relativeOrbit-UAVSAR-TEST-count-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=TEST&output=COUNT"

# season Keyword Invalid
wget -d -O API-TEST-season-negnum-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=-100,-3&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-specchar-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=%,%&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-UA-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=december,may&platform=UA&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-french-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=février,juillet&platform=S1&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-S1-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=march,august&platform=S1&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-negnum-start-end-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=-100,-3&platform=SA,SB&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-specchar-start-end-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=%,%&platform=SA,SB&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-UA-start-end-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=december,may&platform=UA&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-french-S1-start-end-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=février,juillet&platform=S1&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-start-end-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=march,august&platform=S1&start=2020-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-french-now-1weekago-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=février,juillet&platform=S1&start=now&end=1+week+ago&maxresults=1000&output=CSV"
wget -d -O API-TEST-season-months-S1-1weekago-now-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?season=march,august&platform=S1&start=1+week_ago&end=nowtest&maxresults=1000&output=CSV"


# start Keyword Invalid
wget -d -O API-TEST-start-tomorrow-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?start=now&end=1+week+ago&output=CSV
start=tomorrow&end=nowtest&output=CSV"
wget -d -O API-TEST-end-nowtest-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?start=1+week+ago&end=nowtest&output=CSV"
wget -d -O API-TEST-start-now-end-yesterday-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?start=now&end=yesterday&output=CSV"

# queries taken from real world usage Invalid
wget -d -O API-TEST-realworld-9-invalid.csv "https://api-test.asf.alaska.edu/services/search/param?polygon=4794886.03996192,2658783.7409794466,4911667.405803877,2658783.7409794466,4911667.405803877,2775921.3473827764,4794886.03996192,2775921.3473827764,4794886.03996192,2658783.7409794466"
