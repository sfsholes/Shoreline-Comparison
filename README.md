# Shoreline-Comparison
Tool for comparing distance between line shapefiles at different latitudes (Sholes et al. 2020)
This paper is currently "submitted" but in the meantime you can cite Sholes et al. 2019 (Mars 9 Conference Abstract)

Used to compare the differences between mapped shorelines on Mars.
Takes CSV files exported from ArcMap and computes the max latitudinal distance between any of the "shoreline" versions for each longitude within a tolerance (TOL) value.
Uses a moving window of TOL factors (e.g. 2x, 3x) on each side.
ALL INPUT DATA MUST HAVE THE LAST 3 COLUMNS EXACTLY AS:
        Latitude |  Longitude  |  Elevation
    Elevation data can be Null or in meters
    Lat and Lon are in degrees. Lon is E (from -180 to 180)
    
This code can be run from the terminal as is. Adjustments need to be made to the location of the input data. The longitude tolerance value was not used in the paper, but the tool can be used (it provided a negligible difference for sufficiently small TOL, but we tested it just in case). 

CSV files for each of the tested "shorelines" will be uploaded to a permanent repository upon acceptance. 
