#!/bin/bash
clear
LOG_LOCATION=/path/to/my/location/
exec > >(tee -i $LOG_LOCATION/apiprod.log)
exec 2>&1
echo "Starting wget search test cases from api.daac.asf.alaska.edu. Log Location should be: [ $LOG_LOCATION]"

# queries designed just for testing
# absoluteOrbit Keyword
wget -d -O API-PROD-absoluteOrbit-single-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?absoluteorbit=5000&maxresults=10&output=csv"
wget -d -O API-PROD-absoluteOrbit-rangle-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?absoluteorbit=5000-6000&maxresults=10&output=csv"
wget -d -O API-PROD-absoluteOrbit-list-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?absoluteorbit=5000,5001,5002&maxresults=10&output=csv"
wget -d -O API-PROD-absoluteOrbit-list-range-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?absoluteorbit=5000,5100-5200&maxresults=100&output=csv"
wget -d -O API-PROD-absoluteOrbit-list-R1-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?absoluteorbit=5000,5001,5002&platform=R1&maxresults=10&output=csv"

# asfframe Keyword
wget -d -O API-PROD-asfframe-platformR1-single-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?asfframe=345&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-asfframe-platformR1-list-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?asfframe=345,346,347&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-asfframe-platformR1-range-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?asfframe=345-347&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-asfframe-platformR1-list-range-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?asfframe=340,345-347&platform=R1&maxresults=10&output=csv"

# bbox Keyword
wget -d -O API-PROD-bbox-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5&maxresults=10&output=csv"

# beamMode Keyword
wget -d -O API-PROD-beamMode-list-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamMode=FBD,FBS,Standard&maxresults=100&output=csv"
wget -d -O API-PROD-beamMode-Standard-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamMode=Standard&maxresults=10&output=csv"
wget -d -O API-PROD-beamMode-list-R1-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamMode=Standard,STD,Fine,High,Low,Wide,Narrow,ScanSAR+Wide,ScanSAR+Narrow&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-PROD-beamMode-list-S1-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamMode=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1A&maxresults=100&output=csv"
wget -d -O API-PROD-beamMode-list-SB-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamMode=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1B&maxresults=100&output=csv"
wget -d -O API-PROD-beamMode-POL-RPI-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamMode=POL,RPI&maxresults=100&output=csv"


# beamSwath Keyword
wget -d -O API-PROD-beamSwath-1-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=1&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-Airsar-list-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=3FP,ATI,XTI&platform=AIRSAR&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-list-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=FN1,FN2,FN3,FN4,FN5&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-STD-ERS1-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=STD&platform=ERS-1&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-STD-ERS2-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=STD&platform=ERS-2&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-STD-JERS-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=STD&platform=JERS-1&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-STD-SS-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=STD&platform=SEASAT&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-ALOS-list-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=1,2,3,4,5,6,7,8,9,10,11,12,15,16,17,18,19,20&platform=ALOS&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-R1-list-S-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=SNA,SNB,ST1,ST2,ST3,ST4,ST5,ST6,ST7&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-R1-SW-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=SWA,SWB&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-R1-list-WD-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=WD1,WD2,WD3&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-R1-list-E-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=EH3,EH4,EH6,EL1&platform=RADARSAT-1&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-SA-list-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1A&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-SB-list-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=EW,IW,S1,S2,S3,S4,S5,S6,WV&platform=Sentinel-1B&maxresults=100&output=csv"
wget -d -O API-PROD-beamSwath-UA-list-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=UAVSAR&platform=POL,RPI&maxresults=100&output=csv"

# collectionName Keyword
wget -d -O API-PROD-colName-Haiti-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?collectionName=Haiti&maxresults=100&output=csv"
wget -d -O API-PROD-colName-Iceland-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?collectionName=Iceland&maxresults=100&output=csv"
wget -d -O API-PROD-colName-earthquake-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?collectionName=earthquake&maxresults=100&output=csv"
wget -d -O API-PROD-colName-AIRSAR-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?collectionName=AIRSAR&maxresults=100&output=csv"
wget -d -O API-PROD-colName-Denali-100-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?collectionName=Denali&maxresults=100&output=csv"

# end Keyword
wget -d -O API-PROD-end-count-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?end=2005-01-01T00:00:00Z&output=count"
wget -d -O API-PROD-end-now-count-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?end=now&output=count"

# flightDirection Keyword
wget -d -O API-PROD-flightDir-A-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=A&maxresults=10&output=csv"
wget -d -O API-PROD-flightDir-ASC-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=ASC&maxresults=10&output=csv"
wget -d -O API-PROD-flightDir-ASCENDING-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=ASCENDING&maxresults=10&output=csv"
wget -d -O API-PROD-flightDir-D-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=D&maxresults=10&output=csv"
wget -d -O API-PROD-flightDir-DES-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=DESC&maxresults=10&output=csv"
wget -d -O API-PROD-flightDir-DESCENDING-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=DESCENDING&maxresults=10&output=csv"
wget -d -O API-PROD-flightDir-asCEndInG-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=asCEndInG&maxresults=10&output=csv"
wget -d -O API-PROD-flightDir-dEsCeNding-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightDirection=dEsCeNding&maxresults=10&output=csv"

# flightLine Keyword
wget -d -O API-PROD-flightLine-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightLine=15302&maxresults=10&output=csv"
wget -d -O API-PROD-flightLine-gilmorecreek-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?flightLine=gilmorecreek045-1.93044&maxresults=10&output=csv"

# frame Keyword
wget -d -O API-PROD-frame-single-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?frame=345&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-frame-range-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?frame=345-347&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-frame-list-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?frame=345,346,347&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-frame-list-range-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?frame=340,345-347&platform=R1&maxresults=10&output=csv"

# granule_list Keyword
wget -d -O API-PROD-granule_list-single-csv-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=csv"
wget -d -O API-PROD-granule_list-single-count-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=count"
wget -d -O API-PROD-granule_list-single-metalink-valid.metalink "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=metalink"
wget -d -O API-PROD-granule_list-single-kml-valid.kml "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=kml"
wget -d -O API-PROD-granule_list-single-json-valid.json "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=json"
wget -d -O API-PROD-granule_list-single-geo-json-valid.geo.json "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=geo.json"
wget -d -O API-PROD-granule_list-single-download-valid.download "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=download"
wget -d -O API-PROD-granule_list-single-map-valid.map "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80&output=map"

# groupid Keyword
wget -d -O API-PROD-groupid-granuleid-valid.json "https://api.daac.asf.alaska.edu/services/search/param?groupid=S1A_IWDV_0382_0387_019686_014&output=json"
wget -d -O API-PROD-groupid-number-valid.json "https://api.daac.asf.alaska.edu/services/search/param?groupid=12345&output=json"
wget -d -O API-PROD-groupid-hash-valid.json "https://api.daac.asf.alaska.edu/services/search/param?groupid=sdfkhgsdfkhgsdf&output=json"

# intersectswith Keyword
wget -d -O API-PROD-intersectsWith-point-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=point%28-119.543+37.925%29&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-polygon-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=polygon%28%28-119.543 37.925+ -118.443 37.7421+ -118.682 36.8525+ -119.77 37.0352+ -119.543 37.925%29%29&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-linestring-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=linestring(-119.543 37.925, -118.443 37.7421)&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-point-1000-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=point(-119.543,37.925)&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-polygon-10000-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=polygon((-119.543 37.925, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925))&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-polygon2-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=polygon(-119.543 37.925, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925)&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-linestring-invalid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=linestring(TEST)&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-linestring2-invalid.CSV "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=linestring(%)&maxResults=1000&output=CSV"

# linestring Keyword
wget -d -O API-PROD-linestring-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?linestring=-150.2,65.0,-150.1,65.5&maxresults=10&output=csv"

# lookDirection Keyword
wget -d -O API-PROD-lookDir-LEFT-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?lookDirection=LEFT&maxresults=10&output=csv"
wget -d -O API-PROD-lookDir-RIGHT-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?lookDirection=RIGHT&maxresults=10&output=csv"
wget -d -O API-PROD-lookDir-L-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?lookDirection=L&maxresults=10&output=csv"
wget -d -O API-PROD-lookDir-R-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?lookDirection=R&maxresults=10&output=csv"

# maxBaselinePerp Keyword
wget -d -O API-PROD-maxBaselinePerp-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?maxbaselineperp=150&platform=R1&maxresults=10&output=csv"

# maxDoppler Keyword
wget -d -O API-PROD-maxDoppler-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?maxdoppler=2000&platform=R1&maxresults=10&output=csv"

# maxFaradayRotation Keyword
wget -d -O API-PROD-maxFaradayRotation-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?maxfaradayrotation=3&maxresults=10&output=csv"

# maxInsarStackSize Keyword
wget -d -O API-PROD-maxInsarStackSize-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?maxinsarstacksize=50&maxresults=10&output=csv"

# maxResults Keyword
wget -d -O API-PROD-maxResults-1-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=csv"
wget -d -O API-PROD-maxResults-1-valid.json "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=json"
wget -d -O API-PROD-maxResults-1-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=jsonlite"
wget -d -O API-PROD-maxResults-1-valid.geojson "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=1&output=geojson"
wget -d -O API-PROD-maxResults-2-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=csv"
wget -d -O API-PROD-maxResults-2-valid.json "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=json"
wget -d -O API-PROD-maxResults-1-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=jsonlite"
wget -d -O API-PROD-maxResults-2-valid.geojson "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=2&output=geojson"

# minBaselinPerp Keyword
wget -d -O API-PROD-minBaselinePerp-150-10-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?minbaselineperp=150&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-minBaselinPerp-100-150-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?minbaselineperp=100&maxbaselineperp=150&platform=R1&maxresults=10&output=csv"

# minDoppler Keyword
wget -d -O API-PROD-minDoppler1-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?mindoppler=-20000&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-minDoppler2-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?mindoppler=-2000&maxdoppler=2000&platform=R1&maxresults=10&output=csv"

# minFaradayRotation Keyword
wget -d -O API-PROD-minFaradayRot-3-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?minfaradayrotation=3&maxresults=10&output=csv"
wget -d -O API-PROD-minFaradayRot-2-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?minfaradayrotation=2&maxfaradayrotation=3&maxresults=10&output=csv"

# minInsarStackSize Keyword
wget -d -O API-PROD-minInsarStackSize-50-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?mininsarstacksize=50&maxresults=10&output=csv"
wget -d -O API-PROD-minInsarStackSize-80-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?mininsarstacksize=80&maxinsarstacksize=100&maxresults=10&output=csv"

#  offNadirAngle Keyword
wget -d -O API-PROD-offNadirAngle-single-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?offnadirangle=21.5&maxresults=10&output=csv"
wget -d -O API-PROD-offNadirAngle-list-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?offnadirangle=21.5,23.1,27.1&maxresults=10&output=csv"
wget -d -O API-PROD-offNadirAngle-range-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?offnadirangle=20-30&maxresults=10&output=csv"

# output keyword
wget -d -O API-PROD-platform-SB-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=csv"
wget -d -O API-PROD-platform-SB-count-valid.CSV "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=count"
wget -d -O API-PROD-platform-SB-download-valid.download "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=download"
wget -d -O API-PROD-platform-SB-geojson-valid.geojson "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=geojson"
wget -d -O API-PROD-platform-SB-json-valid.json "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=json"
wget -d -O API-PROD-platform-SB-jsonlite-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=jsonlite"
wget -d -O API-PROD-platform-SB-kml-valid.kml "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=kml"
wget -d -O API-PROD-platform-SB-metalink-valid.metalink "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=metalink"

# pagesize + jsonlite output
wget -d -O API-PROD-pagesize-R1-E1-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=R1,E1&pagesize=1000&output=jsonlite"

# platform Keyword
wget -d -O API-PROD-platform-SA-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SA&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"
wget -d -O API-PROD-platform-SB-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1+week+ago&end=now&maxresults=2000&output=csv"
wget -d -O API-PROD-platform-J1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=J1&polygon=-148.52,64.63,-150.41,64.64,-149.58,63.86,-148.52,64.63&maxResults=100&output=csv"
wget -d -O API-PROD-platform-A3-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=A3&processinglevel=L1.0polygon=-148.52,64.63,-150.41,64.64,-149.58,63.86,-148.52,64.63&maxResults=100&output=csv"
wget -d -O API-PROD-platform-Sentinel-1A-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel-1A&maxResults=10&output=csV"
wget -d -O API-PROD-platform-R1-E1-valid.json "https://api.daac.asf.alaska.edu/services/search/param?platform=R1,E1&maxResults=10&output=jSoN"
wget -d -O API-PROD-platform-R1-E1-10-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=RADARSAT-1,E1&maxResults=10&output=csv"
wget -d -O API-PROD-platform-R1-E1-L0-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=RADARSAT-1,E1&processingLEVEL=L0,L1&maxResults=10&output=csv"
wget -d -O API-PROD-platform-SP-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SP&maxResults=10&output=csv"
wget -d -O API-PROD-platform-UA-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UA&maxResults=10&output=csv"
wget -d -O API-PROD-platform-E1E2-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=E1,E2&maxResults=10&output=csv"

# platform aliases + count output
wget -d -O API-PROD-platform-S1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=S1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SENTINEL1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Sentinel-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-s-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=s-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-ERS-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ERS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-erS-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=erS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-R1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=R1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-r1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=r1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-RADARSAT-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=RADARSAT-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Radarsat-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Radarsat-1&start=2016-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-E1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=E1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-ERS-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ERS-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Ers-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Ers-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-E2-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=E2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-ERS-2-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ERS-2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-e2-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=e2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-ers-2-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ers-2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-J1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=J1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-JERS-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=JERS-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Jers-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Jers-1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-j1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=j1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-A3-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=A3&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-ALOS-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ALOS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-a3-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=a3&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-alos-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=alos&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Alos-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Alos&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-AS-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=AS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-DC8-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=DC-8&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-AIRSAR-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=AIRSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Airsar-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Airsar&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-as-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=as&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-AiRSAR-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=AiRSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-dc-8-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=dc-8&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SS-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SEASAT-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SEASAT%201&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SEASAT-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SEASAT&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-ss-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ss&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Seasat-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Seasat&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SeaSAT-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SeaSAT%201&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SA-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SA&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Sentinel-1A-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel-1A&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-sa-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=sa&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-sentinel-1a-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=sentinel-1a&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SENTINEL-1A-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1A&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Sb-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sb&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SB-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SB&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Sentinel-1B-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel-1B&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SB-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1B&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SP-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SP&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Sp-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sp&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-sp-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=sp&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-SMAP-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SMAP&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Smap-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Smap&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-smap-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=smap&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-UA-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UA&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-ua-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ua&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-Ua-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Ua&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-UAVSAR-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAVSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-UAvSAR-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAvSAR&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-G-III-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=G-III&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform-g-iii-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=g-iii&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"

# platform_list Keyword
wget -d -O API-PROD-platform_list-lc-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=sentinel,ers&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-uc-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=SENTINEL,ERS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-aliases-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=S1,Ers&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-aliases-uc-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=J1,ERS&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-uc2-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=JERS-1,ERs&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-E1E2-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=E1,E2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-ERS12-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=ERS-1,ERs-2&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-S1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=S1&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"
wget -d -O API-PROD-platform_list-SASB-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=SA,Sb&start=1978-01-01T00:00:00Z&end=2018-01-02T00:00:00Z&output=count"


# point Keyword
wget -d -O API-PROD-point-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?point=-150.2,65.0&maxresults=10&output=csv"

# polarization Keyword
wget -d -O API-PROD-polar-HH-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=HH&platform=SA&maxresults=10&output=csv"
wget -d -O API-PROD-polar-VV-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=VV&platform=SA&maxresults=10&output=csv"
wget -d -O API-PROD-polar-HH-HV-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=HH%2bHV&maxresults=10&output=csv"
wget -d -O API-PROD-polar-DualVV-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Dual+VV&maxresults=10&output=csv"
wget -d -O API-PROD-polar-QUADRATURE-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=QUADRATURE&maxresults=10&output=csv"
wget -d -O API-PROD-polar-VV-VH-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=VV%2bVH&maxresults=10&output=csv"
wget -d -O API-PROD-polar-DualHV-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Dual+HV&maxresults=10&output=csv"
wget -d -O API-PROD-polar-DualVH-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Dual+VH&maxresults=10&output=csv"
wget -d -O API-PROD-polar-DualVH-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Dual+VH&maxresults=10&output=csv"
wget -d -O API-PROD-polar-hH-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=hH&platform=SA&maxresults=10&output=csv"
wget -d -O API-PROD-polar-Vv-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Vv&platform=SA&maxresults=10&output=csv"
wget -d -O API-PROD-polar-Hh-hV-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Hh%2bhV&maxresults=10&output=csv"
wget -d -O API-PROD-polar-Dualvv-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Dual+vv&maxresults=10&output=csv"
wget -d -O API-PROD-polar-quadrature-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=quadrature&maxresults=10&output=csv"
wget -d -O API-PROD-polar-vv-VH-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=vv%2bVH&maxresults=10&output=csv"
wget -d -O API-PROD-polar-Dualhv-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=Dual+hv&maxresults=10&output=csv"
wget -d -O API-PROD-polar-dualVH-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=dual+VH&maxresults=10&output=csv"
wget -d -O API-PROD-polar-dualvh-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polarization=dual+vh&maxresults=10&output=csv"

# polygon Keyword
wget -d -O API-PROD-polygon-multi-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=12.13,41.74,13.4,41.74,13.4,42.75,12.13,42.75,12.13,41.74&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"
wget -d -O API-PROD-polygon-4-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=-148.52,64.63,-150.41,64.64,-149.58,63.86,-148.52,64.63&maxResults=100&output=csv"

# processingLevel Keyword
wget -d -O API-PROD-procLevel-L11-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=L1.1&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-L11-L1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=L1.1,L1.0&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-list-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=3FP,ATI,LTIF,PTIF,CTIF,PSTOKES,BROWSE,DEM,CSTOKES,JPG,LSTOKES,THUMBNAIL&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-RTC-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=RTC_LOW_RES,RTC_HI_RES&platform=ALOS&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-ERS-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=L0,L1,BROWSE,THUMBNAIL&platform=ERS-1,ERS-2&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-JERS1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=L0,L1,BROWSE,THUMBNAIL&platform=JERS-1&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-R1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=L0,L1,BROWSE,THUMBNAIL&platform=RADARSAT-1&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-SS-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=L1,BROWSE,THUMBNAIL&platform=SEASAT&maxResults=10&output=CSV"
wget -d -O API-PROD-procLevel-S1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=METADATA_GRD,GRD_HS,GRD_HD,GRD_MS,GRD_MD,GRD_FS,GRD_FD,SLC,RAW,OCN,METADATA_RAW,METADATA,METADATA_SLC, THUMBNAIL&platform=Sentinel-1A,Sentinel-1B&maxResults=100&output=CSV"
wget -d -O API-PROD-procLevel-SMAP-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=L1A_Radar_RO_QA,L1B_S0_LoRes_HDF5,L1B_S0_LoRes_QA,L1B_S0_LoRes_ISO_XML,L1A_Radar_QA,L1A_Radar_RO_ISO_XML, L1C_S0_HiRes_ISO_XML,L1C_S0_HiRes_QA,L1C_S0_HiRes_HDF5,L1A_Radar_HDF5&platform=SMAP&maxResults=100&output=CSV"
wget -d -O API-PROD-procLevel-UA-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=KMZ,PROJECTED,PAULI,PROJECTED_ML5X5,STOKES,AMPLITUDE,BROWSE,COMPLEX,DEM_TIFF,PROJECTED_ML3X3,METADATA,AMPLITUDE_GRD,INTERFEROMETRY,INTERFEROMETRY_GRD,THUMBNAIL&platform=UAVSAR&maxResults=100&output=CSV"


# processingDate Keyword
wget -d -O API-PROD-procDate-Z-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingDate=2018-01-01T00:00:00Z&maxresults=10&output=csv"
wget -d -O API-PROD-procDate-yesterday-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingDate=yesterday&maxresults=10&output=csv"
wget -d -O API-PROD-procDate-weekago-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingDate=1+week+ago&maxresults=10&output=csv"
wget -d -O API-PROD-procDate-today-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingDate=today&maxresults=10&output=csv"
wget -d -O API-PROD-procDate-monthago-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingDate=1+month+ago&maxresults=10&output=csv"
wget -d -O API-PROD-procDate-2monthago-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingDate=2+month+ago&maxresults=10&output=csv"

# product_list Keyword
wget -d -O API-PROD-product_list-S1-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040550_20141003T040619_002660_002F64_EC04-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040644_20141003T040709_002660_002F64_9E20-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040709_20141003T040734_002660_002F64_4C78-GRD_HD,S1A_IW_GRDH_1SDV_20141003T040734_20141003T040754_002660_002F64_288E-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053708_20141003T053737_002661_002F66_A2F4-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053737_20141003T053802_002661_002F66_6132-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053802_20141003T053827_002661_002F66_18D8-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053827_20141003T053852_002661_002F66_5DF0-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053852_20141003T053917_002661_002F66_C3AA-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053917_20141003T053942_002661_002F66_014F-GRD_HD,S1A_IW_GRDH_1SDV_20141003T053942_20141003T054007_002661_002F66_7F10-GRD_HD,S1A_IW_GRDH_1SDV_20141003T054007_20141003T054032_002661_002F66_825E-GRD_HD&output=jsonlite"
wget -d -O API-PROD-product_list-mix-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD&product_list=ALPSRP016350310-L1.5,ALPSRP016350320-L1.5,ALPSRP016350330-L1.5,ALPSRP016350340-L1.5,ALPSRP016350350-L1.5,ALPSRP016350360-L1.5,ALPSRP016350370-L1.5,ALPSRP016350380-L1.5&output=jsonlite"
wget -d -O API-PROD-product_list-multi-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD&product_list=ALPSRP016350310-L1.5&product_list=E2_23229_STD_F285-L0&product_list=R1_14387_ST5_F281-L0&product_list=E1_24859_STD_F703-L0&output=jsonlite"
wget -d -O API-PROD-product_list-multi2-valid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?product_list=S1A_IW_GRDH_1SDV_20171213T155548_20171213T155613_019686_021746_FC80-GRD_HD&product_list=E2_18061_STD_F277-L1,E2_18061_STD_F315-L1,E2_18061_STD_F259-L1,E2_18061_STD_F295-L1&output=jsonlite"

# relativeOrbit Keyword
wget -d -O API-PROD-relativeOrbit-single-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeorbit=20&maxresults=10&output=csv"
wget -d -O API-PROD-relativeOrbit-range-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeorbit=20-22&maxresults=10&output=csv"
wget -d -O API-PROD-relativeOrbit-list-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeorbit=20,21,22&maxresults=10&output=csv"
wget -d -O API-PROD-relativeOrbit-list-range-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeorbit=20,23-24&maxresults=100&output=csv"
wget -d -O API-PROD-relativeOrbit-list-R1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeorbit=20,23,25&platform=R1&maxresults=10&output=csv"

# season Keyword
wget -d -O API-PROD-season-32-90-S1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-100-S1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-175-UA-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,175&platform=UA&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-32-90-S1-start-end-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&start=2017-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-100-S1-start-end-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&start=2015-01-01T00:00:00Z&end=2018-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-175-UA-start-end-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,175&platform=UA&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-32-90-S1-1weekago-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&start=1+week+ago&end=now&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-100-S1-1weekago-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&start=1+week+ago&end=now&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-175-UA-july2018-now-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,175&platform=UA&start=2018-July-15&end=now&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-32-90-S1-july2018-now-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=32,90&platform=SA,SB&start=2018-July-15&end=now&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-100-S1-yesterday-now-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,100&platform=SA,SB&start=yesterday&end=now&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-1-100-UA-monthago-now-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=1,175&platform=UA&start=1+month+ago&end=now&maxresults=1000&output=CSV"

# start Keyword
wget -d -O API-PROD-start-Zdate-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=2005-01-01T00:00:00Z&output=count"
wget -d -O API-PROD-start-Zdate-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=2005-01-01T00:00:00Z&end=2005-01-01T01:00:00Z&output=csv"
wget -d -O API-PROD-start-3monthagoplus1day-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=3+months+and+a+day+ago&output=count"
wget -d -O API-PROD-start-june302018-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=June+30,+2018&output=count"
wget -d -O API-PROD-start-weekago-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=week+ago&output=count"
wget -d -O API-PROD-start-dayago-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=day+ago&output=count"
wget -d -O API-PROD-start-today-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=today&output=count"
wget -d -O API-PROD-start-yesterday-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=yesterday&output=count"


# new formats

# polygon closure/winding order fixer test
wget -d -O API-PROD-polygonclosure1-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=12.13,41.74,13.4,41.74,13.4,42.75,12.13,42.75&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"
wget -d -O API-PROD-polygonclosure2-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=12.13,41.74,13.4,41.74,13.4,42.75,12.13,42.75,12.13,41.74&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"
wget -d -O API-PROD-polygonclosure3-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=12.13,41.74,12.13,42.75,13.4,42.75,13.4,41.74,12.13,41.74&platform=Sentinel-1A,Sentinel-1B&processingLevel=SLC&start=2018-05-01T00:00:00UTC&output=csv"

# queries taken from real-world usage
wget -d -O API-PROD-realworld-1-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=point(-168.0380672+53.9279675)&platform=Sentinel-1A,Sentinel-1B&processingLevel=GRD_HS,GRD_HD&beamMode=IW&output=count"
wget -d -O API-PROD-realworld-2-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=linestring(-102+37.59,-94+37,-94+39,-102+39)&platform=Sentinel-1A,Sentinel-1B&processingLevel=GRD_HS,GRD_HD&beamMode=IW&output=count"
wget -d -O API-PROD-realworld-3-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=polygon((-102+37.59,-94+37,-94+39,-102+39,-102+37.59))&platform=Sentinel-1A,Sentinel-1B&processingLevel=GRD_HS,GRD_HD&beamMode=IW&output=count"
wget -d -O API-PROD-realworld-4-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?output=count&frame=587%2C588%2C589%2C590%2C591%2C592%2C593&processingLevel=L0%2CL1.0%2CSLC&platform=SENTINEL-1A%2CSENTINEL-1B&maxResults=1000&relativeOrbit=128"
wget -d -O API-PROD-realworld-5-count-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?output=count&asfframe=587%2C588%2C589%2C590%2C591%2C592%2C593&processingLevel=L0%2CL1.0%2CSLC&platform=SENTINEL-1A%2CSENTINEL-1B&maxResults=1000&relativeOrbit=128"
wget -d -O API-PROD-realworld-6-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SA,SB&relativeOrbit=128&asfframe=587-593&start=2017-06-01&end=2018-05-30&output=csv"
wget -d -O API-PROD-realworld-7-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SA,SB&relativeOrbit=128&frame=587-593&start=2017-06-01&end=2018-05-30&output=csv"
wget -d -O API-PROD-realworld-8-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?output=csv&platform=Sentinel-1A&start=2018-05-30&end=2018-05-31%22"
wget -d -O API-PROD-realworld-9-valid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=4794886.03996192,2658783.7409794466,4911667.405803877,2658783.7409794466,4911667.405803877,2775921.3473827764,4794886.03996192,2775921.3473827764,4794886.03996192,2658783.7409794466"


### Negative Tests ###
# invalid queries
wget -d -O API-PROD-invalid-query.csv "https://api.daac.asf.alaska.edu/services/search/param?output=csv&maxresults=10"
wget -d -O API-PROD-missing-query.csv "https://api.daac.asf.alaska.edu/services/search/param"


### Negative Tests ###
# absoluteOrbit Keyword Invalid
wget -d -O API-PROD-absoluteOrbit-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?absoluteorbit=TEST&maxresults=10&output=csv"
wget -d -O API-PROD-absoluteOrbit-specch-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?absoluteorbit=@&maxresults=10&output=csv"

# asfframe Keyword Invalid
wget -d -O API-PROD-asfframe-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?asfframe=TEST&maxresults=10&output=csv"
wget -d -O API-PROD-asfframe-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?asfframe=$&maxresults=10&output=csv"

# bbox Keyword Invalid
wget -d -O API-PROD-bbox-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?bbox=TEST&output=CSV"
wget -d -O API-PROD-bbox-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?bbox=$&output=CSV"
wget -d -O API-PROD-bbox-incomplete-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=CSV"
wget -d -O API-PROD-bbox-incomplete-json-invalid.json "https://api.daac.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=JSON"
wget -d -O API-PROD-bbox-incomplete-jsonlite-invalid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=JSONLITE"
wget -d -O API-PROD-bbox-incomplete-geojson-invalid.geojson "https://api.daac.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1,65.5,0&output=GEO.JSON"
wget -d -O API-PROD-bbox-incomplete-download-invalid.download "https://api.daac.asf.alaska.edu/services/search/param?bbox=-150.2,65.0,-150.1&output=download"

# beamMode Keyword Invalid
wget -d -O API-PROD-beamMode-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?beamMode=#&output=CSV"
wget -d -O API-PROD-beamMode-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?beamMode=TEST&output=CSV"
wget -d -O API-PROD-beamMode-TEST-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?beamMode=TEST&output=CSV,COUNT"
wget -d -O API-PROD-beamMode-specchar2-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?beamMode=@&output=CSV"

# beamSwath Keyword Invalid
wget -d -O API-PROD-beamSwath-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=TEST&output=CSV"
wget -d -O API-PROD-beamSwath-TEST-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=TEST&output=CSV,COUNT"
wget -d -O API-PROD-beamSwath-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?beamSwath=@&output=CSV"

# collectionName Keyword Invalid
wget -d -O API-PROD-collectionName-A3-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ALOS&collectionName=TEST&output=CSV"
wget -d -O API-PROD-collectionName-UA-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAVSAR&collectionName=TEST&output=CSV"
wget -d -O API-PROD-collectionName-S1-ABoVE-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1A&collectionName=ABoVE&output=CSV"
wget -d -O API-PROD-collectionName-S1-Alaska-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&collectionName=Alaska&output=CSV"
wget -d -O API-PROD-collectionName-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?collectionName=$&output=CSV"

# end Keyword Invalid
wget -d -O API-PROD-end-2020Z-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?end=2020-01-01T00:00:00Z&output=count"
wget -d -O API-PROD-end-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?end=@%&output=count"

# flightDirection Keyword Invalid
wget -d -O API-PROD-flightDir-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=E1&flightDirection=TEST&beamMode=STD&maxResults=100&output=CSV"
wget -d -O API-PROD-flightDir-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=E1&flightDirection=$&beamMode=STD&maxResults=100&output=CSV"

# flightLine Keyword Invalid
wget -d -O API-PROD-flightLine-UA-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAVSAR&flightLine=TEST&output=CSV"
wget -d -O API-PROD-flightLine-AS-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=AIRSAR&flightLine=TEST&output=CSV"
wget -d -O API-PROD-flightLine-AS-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=AIRSAR&flightLine=$&output=CSV"

# frame Keyword Invalid
wget -d -O API-PROD-frame-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ALOS&frame=TEST&maxResults=100&output=CSV"
wget -d -O API-PROD-frame-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=ALOS&frame=@&maxResults=100&output=CSV"

# granule_list Keyword Invalid
wget -d -O API-PROD-granule_list-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?granule_list=TEST&output=CSV"
wget -d -O API-PROD-granule_list-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?granule_list$#@$&output=CSV"

# groupid Keyword Invalid
wget -d -O API-PROD-groupid-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?groupid=TEST&output=csv"
wget -d -O API-PROD-groupid-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?groupid=$#&output=csv"

# intersectsWith  Keyword Invalid
wget -d -O API-PROD-intersectsWith-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=linestring(TEST)&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=linestring(%)&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-point-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=point(TEST,37.925)&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-polygon-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=polygon((TEST 37.925, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925))&maxResults=1000&output=CSV"
wget -d -O API-PROD-intersectsWith-polygon-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?intersectsWith=polygon($ $, -118.443 37.7421, -118.682 36.8525, -119.77 37.0352, -119.543 37.925)&maxResults=1000&output=CSV"


# linestring Keyword Invalid
wget -d -O API-PROD-linestring-num-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?linestring=-150.2,65.0,#&maxresults=10&output=csv"
wget -d -O API-PROD-linestring-TEST-FAIL-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?linestring=TEST,FAIL&maxresults=10&output=csv"
wget -d -O API-PROD-linestring-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?linestring(TEST)&maxResults=1000&output=CSV"
wget -d -O API-PROD-linestring-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?linestring(%)&maxResults=1000&output=CSV"

# lookDirection Keyword Invalid
wget -d -O API-PROD-lookDir-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?lookDirection=TEST&maxResults=1000&output=CSV"
wget -d -O API-PROD-lookDir-1-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?lookDirection=1&maxResults=1000&output=CSV"

# maxBaselinePerp Keyword Invalid
wget -d -O API-PROD-maxBaseLinePerp-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?maxbaselineperp=%&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-maxBaseLinePerp-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?maxbaselineperp=TEST&platform=R1&maxresults=10&output=csv"

# maxDoppler Keyword Invalid
wget -d -O API-PROD-maxDoppler-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxDoppler=TEST&output=CSV"
wget -d -O API-PROD-maxDoppler-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxDoppler=@&output=CSV"

# maxFaradayRotation Keyword Invalid
wget -d -O API-PROD-maxFaradayRotation-0-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=0&output=CSV"
wget -d -O API-PROD-maxFaradayRotation-neg-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=-5.0&output=CSV"
wget -d -O API-PROD-maxFaradayRotation-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=TEST&output=CSV"
wget -d -O API-PROD-maxFaradayRotation-empty-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=&output=CSV"
wget -d -O API-PROD-maxFaradayRotation-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=***&output=CSV"

# maxInsarStackSize Keyword Invalid
wget -d -O API-PROD-maxInsarStackSize-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL&maxInsarStackSize=#&maxResults=100&output=CSV"
wget -d -O API-PROD-maxInsarStackSize-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL&maxInsarStackSize=TEST&maxResults=100&output=CSV"

# maxResults Keyword Invalid
wget -d -O API-PROD-maxResults-0-invalid.CSV "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=csv"
wget -d -O API-PROD-maxResults-0-invalid.json "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=json"
wget -d -O API-PROD-maxResults-0-invalid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=jsonlite"
wget -d -O API-PROD-maxResults-0-invalid.geojson "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=0&output=geojson"
wget -d -O API-PROD-maxResults-a-invalid.CSV "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=csv"
wget -d -O API-PROD-maxResults-a-invalid.json "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=json"
wget -d -O API-PROD-maxResults-a-invalid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=jsonlite"
wget -d -O API-PROD-maxResults-a-invalid.geojson "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=a&output=geojson"
wget -d -O API-PROD-maxResults-%-invalid.CSV "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=csv"
wget -d -O API-PROD-maxResults-%-invalid.json "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=json"
wget -d -O API-PROD-maxResults-%-invalid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=jsonlite"
wget -d -O API-PROD-maxResults-%-invalid.geojson "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&maxresults=%&output=geojson"

# minBaselinPerp Keyword Invalid
wget -d -O API-PROD-minBaselineperp-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?minbaselineperp=TEST&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-minBaselineperp-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?minbaselineperp=%%%&platform=R1&maxresults=10&output=csv"

# minDoppler Keyword Invalid
wget -d -O API-PROD-minDoppler-negnum-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?mindoppler=-20000&platform=R1&maxresults=10&output=csv"
wget -d -O API-PROD-minDoppler-negnum2-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?mindoppler=-2000&maxdoppler=2000&platform=R1&maxresults=10&output=csv"

# minFaradayRotation Keyword Invalid
wget -d -O API-PROD-minFaradayRot-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?minfaradayrotation=#&maxresults=10&output=csv"
wget -d -O API-PROD-minFaradayRot-specchar2-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?minfaradayrotation=#&maxfaradayrotation=#&maxresults=10&output=csv"
wget -d -O API-PROD-minFaradayRot-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?minfaradayrotation=TEST&maxfaradayrotation=TEST&maxresults=10&output=csv"
wget -d -O API-PROD-minFaradayRot-0-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=0&output=CSV"
wget -d -O API-PROD-minFaradayRot-neg5-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&maxFaradayRotation=-5.0&output=CSV"
wget -d -O API-PROD-minFaradayRot-specchar2-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&minFaradayRotation=&output=CSV"
wget -d -O API-PROD-minFaradayRot-specchar3-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=Sentinel&minFaradayRotation=***&output=CSV"

# minInsarStackSize Keyword Invalid
wget -d -O API-PROD-minInsarStackSize-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?mininsarstacksize=$&maxresults=10&output=csv"
wget -d -O API-PROD-minmaxInsarStackSize-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?mininsarstacksize=$&maxinsarstacksize=#&maxresults=10&output=csv"
wget -d -O API-PROD-minmaxInsarStackSize-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?mininsarstacksize=TEST&maxinsarstacksize=TEST&maxresults=10&output=csv"

#  offNadirAngle Keyword Invalid
wget -d -O API-PROD-offNadirAngle-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?offNadirAngle=TEST&maxResults=1000&output=CSV"
wget -d -O API-PROD-offNadirAngle-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?offNadirAngle=$&maxResults=1000&output=CSV"

# output Keyword Invalid
wget -d -O API-PROD-output-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=05905-05906&output=TEST"
wget -d -O API-PROD-output-SCS-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=05905-05906&maxResults=1/2&output=CSC"

# pagesize Invalid + jsonlite output
wget -d -O API-PROD-pagesize-invalid.jsonlite "https://api.daac.asf.alaska.edu/services/search/param?platform=R1,E1&pagesize=TEST&output=jSoNlite"

# platform Keyword Invalid
wget -d -O API-PROD-platform-specchar1-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=@&maxResults=10&output=CSV"
wget -d -O API-PROD-platform-specchar1-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=@&maxResults=10&output=COUNT"
wget -d -O API-PROD-platform-specchar2-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=~&maxResults=10&output=COUNT"
wget -d -O API-PROD-platform-specchar3-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=%&maxResults=10&output=COUNT"
wget -d -O API-PROD-platform-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=TEST&maxResults=10&output=COUNT"

# platform aliases Keyword Invalid
wget -d -O API-PROD-platform-aliases-S2-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=S2&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"
wget -d -O API-PROD-platform-aliases-SENTI-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=SENTI&start=1+week+ago&end=now&maxresults=2000&output=csv"
wget -d -O API-PROD-platform-aliases-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=TEST&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"

# platform_list Keyword Invalid
wget -d -O API-PROD-platform_list-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=Test,TEST&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"
wget -d -O API-PROD-platform_list-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform_list=#,$&start=2016-01-01T00:00:00Z&end=2016-01-02T00:00:00Z&output=csv"

# point Keyword Invalid
wget -d -O API-PROD-point-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?point=-150.2&maxresults=10&output=csv"
wget -d -O API-PROD-point-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?point=$#&maxresults=10&output=csv"

# polarization Keyword Invalid
wget -d -O API-PROD-polar-numb-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=AIRSAR&polarization=12&output=CSV"
wget -d -O API-PROD-polar-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=AIRSAR&polarization=%@#&output=CSV"
wget -d -O API-PROD-polar-E1-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=E1&polarization=^*&maxResults=1000&output=CSV"

# polygon Keyword Invalid
wget -d -O API-PROD-polygon-broken-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=-155.08,65.82,-153.5,61.91,-149.50,63.07,-149.94,64.55&maxResults=1000&output=CSV"
wget -d -O API-PROD-polygon-3points-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=-155.08,65.82,-153.5&maxResults=1000&output=CSV"
pwget -d -O API-PROD-polygon-1point-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?olygon=-155.08,65.82&maxResults=1000&output=CSV"
wget -d -O API-PROD-polygon-1point-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=-155.08,65.82&maxResults=1000&output=count"
wget -d -O API-PROD-polygon-specchar-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=$$&maxResults=1000&output=count"
wget -d -O API-PROD-polygon-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=$$&maxResults=1000&output=CSV"
wget -d -O API-PROD-polygon-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?polygon=TEST&maxResults=1000&output=CSV"


# processingLevel Keyword Invalid
wget -d -O API-PROD-procLevel-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=@@&maxResults=1000&output=CSV"
wget -d -O API-PROD-procLevel-LSTOKETS-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingLevel=LSTOKETS&&output=COUNT"

# processingDate Keyword Invalid
wget -d -O API-PROD-procDate-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?processingDate=$$$&maxResults=1200&output=CSV"

# product_list Invalid + CSV output
wget -d -O API-PROD-product_list-numb-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?product_list=0,1,2,3,4&output=CSV"
wget -d -O API-PROD-product_list-alpha-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?product_list=a,b,c,d&output=CSV"
wget -d -O API-PROD-product_list-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?product_list=#,$,%,@&output=CSV"
wget -d -O API-PROD-product_list-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?product_list=TEST,INVALID&output=CSV"

# relativeOrbit Keyword Invalid
wget -d -O API-PROD-relativeOrbit-671-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeOrbit=671&output=CSV"
wget -d -O API-PROD-relativeOrbit-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeOrbit=TEST&output=CSV"
wget -d -O API-PROD-relativeOrbit-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?relativeOrbit=@@&output=CSV"
wget -d -O API-PROD-relativeOrbit-UA-TEST-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=TEST&output=CSV"
wget -d -O API-PROD-relativeOrbit-UAVSAR-TEST-count-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?platform=UAVSAR&relativeOrbit=TEST&output=COUNT"

# season Keyword Invalid
wget -d -O API-PROD-season-negnum-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=-100,-3&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-specchar-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=%,%&platform=SA,SB&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-UA-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=december,may&platform=UA&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-french-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=février,juillet&platform=S1&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-S1-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=march,august&platform=S1&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-negnum-start-end-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=-100,-3&platform=SA,SB&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-specchar-start-end-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=%,%&platform=SA,SB&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-UA-start-end-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=december,may&platform=UA&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-french-S1-start-end-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=février,juillet&platform=S1&start=2005-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-start-end-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=march,august&platform=S1&start=2020-01-01T00:00:00Z&end=2019-01-01T01:00:00Z&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-french-now-1weekago-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=février,juillet&platform=S1&start=now&end=1+week+ago&maxresults=1000&output=CSV"
wget -d -O API-PROD-season-months-S1-1weekago-now-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?season=march,august&platform=S1&start=1+week_ago&end=nowtest&maxresults=1000&output=CSV"


# start Keyword Invalid
wget -d -O API-PROD-start-tomorrow-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=now&end=1+week+ago&output=CSV
start=tomorrow&end=nowtest&output=CSV"
wget -d -O API-PROD-end-nowtest-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=1+week+ago&end=nowtest&output=CSV"
wget -d -O API-PROD-start-now-end-yesterday-invalid.csv "https://api.daac.asf.alaska.edu/services/search/param?start=now&end=yesterday&output=CSV"
