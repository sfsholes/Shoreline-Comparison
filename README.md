# Shoreline-Comparison
Tool for comparing distance between line shapefiles at different latitudes (Sholes et al. 2020)
This paper is currently in review at the Journal of Geophysical Research: Planets but in the meantime you can cite the preprint Sholes et al. (2020): "Where are Mars' Hypothesized Ocean Shorelines? Large Lateral and Topographic Offsets Between Different Versions of Paleoshoreline Maps." https://doi.org/10.1002/essoar.10502868.1

Used to compare the differences between mapped shorelines on Mars.
Takes CSV files exported from ArcMap (with LAT, LON, and Geodesic Length) and computes the minimum latitudinal distance between all tested maps of the "shoreline" versions. 

Imported data uses both a perpendicular method (where geodesic distances are calculated perpendicular to the outermost mapped levels) and a longitudinal method (where geodeisc distances are calculated along lines of longitude), with a pass for the plainsward-side and the highlands-side mappings. 
    
This code can be run from the terminal as is. Adjustments need to be made to the location of the input data. 

All the data are uploaded to Sholes et al. (2020): https://doi.org/10.5281/zenodo.4035601
