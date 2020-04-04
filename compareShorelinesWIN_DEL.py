# compareShorelinesWIN.py
# by Steven F. Sholes
# sfsholes@uw.edu
# Updated: Apr. 3, 2020

# Used to compare the differences between mapped shorelines
# Takes CSV files exported from ArcMap and computes the max 
#   latitudinal distance between any of the shorelines
#   for each longitude within a tolerance (TOL) value.
#   Uses a moving window of TOL factors (e.g. 2x, 3x) on
#   each side.
# ALL INPUT DATA MUST HAVE THE LAST 3 COLUMNS EXACTLY AS:
#        Latitude |  Longitude  |  Elevation
#    Elevation data can be Null or in meters
#    Lat and Lon are in degrees. Lon is E (from -180 to 180)


import csv
import os
import math
import matplotlib.pyplot as plt
import numpy as np
from geopy import distance

PATH = "D://Research//05_GlobalMarsShorelines//1_Input//CitedShorelines//ZachRemaps//PointsOutput"
TOL = 0.25         # Tolerance for Longitude increments (in degrees)

## Go through all inputs in the directory to find the range
LON_LIST = []        # Stores all the longitude values we are checking
TUP_LIST = []        # Stores all the tuples from all files
MAX_LIST = []        # Will store all max point tuples
MIN_LIST = []        # Will store all the min point tubles
DIFF_LIST = []       # Will store tuples (LAT DIFF, LON)

# Open the CSV files in the PATH directory
# Builds THE LON and TUP LISTS for analysis
file_num = 0        # This labels each shoreline file
for filename in os.listdir(os.path.join(PATH,"data")):
    # FINDS ALL TXT AND CSV FILES IN DIRECTORY TO OPEN
    if filename.endswith(".txt") or filename.endswith(".csv"):
        print("OPENING..." + filename)
        file = open(os.path.join(PATH,"data",filename), newline='')
        reader = csv.reader(file)
        header = next(reader)       # The first line is the header
        
        data = []
        for row in reader:
            # row = [OBID, FID, NAME, LENGTH, LAT, LON]
            LON = float(row[-1])
            LON_ROUND = round(LON*(1/TOL))/(1/TOL)      #Rounds to nearest TOL
            # TODO - ABOVE COULD CAUSE MINOR PROBLEMS, BUT SHOULD BE MINIMAL
            LAT = float(row[-2])
            LON_LIST.append(LON_ROUND)
            # GENERATE A LIST OF ALL TOTAL POINTS
            TUP_LIST.append((LAT, LON_ROUND, file_num))
        file_num += 1
    else:
        continue

print("Total points: ", len(TUP_LIST))

def distConv(p1, p2):
    """Takes two tuples (p1 and p2) of x,y coordiates in decimal degrees
    and converts that distance to kilometers"""
    D = 3376.2   #Mars diameter in km
    # GeoPy uses Earth params, so modifying to MOLA sphere
    # Same as geodesic measurements in ArcMap
    dist = distance.distance(p1,p2,ellipsoid=(D,D,0)).km
    return dist

# Compares all the datapoints to find the max descrepancy for each LON
LON_LIST_UNIQ = list(set(LON_LIST))        #Removes duplicates and sorts
LON_LIST_UNIQ.sort()

####################################################################
        ###      FIND MIN/MAX LATITUDES AT LONGS      ###
####################################################################

# 1) Go through each lon and find the max/min pairs
for item in LON_LIST_UNIQ:
    # Make a list of all tuples with the LON we are examining
    TUP_LIST_TEMP = [j for i, j in enumerate(TUP_LIST) if j[1] == item]
    # i is the enumerate value (0,1,2...), j is the tuple (0=lat, 1=lon_round, 2=file)
    
    if len(TUP_LIST_TEMP) == 0:        #Check for empty set
        max_lat_tup = Null
        min_lat_tup = Null
        lat_diff = Null
    elif len(TUP_LIST_TEMP) == 1:        #When there is only one point for that longitude
        max_lat_tup = TUP_LIST_TEMP[0]
        min_lat_tup = TUP_LIST_TEMP[0]
        lat_diff = 0
    else:                               # For all normal points
        # SET UP PERMANENT VARIABLES
        # Finds the max/min lat of each long (item[0] is that lat)
        OVERALL_MAX = max(TUP_LIST_TEMP, key=lambda item:item[0])
        OVERALL_MIN = min(TUP_LIST_TEMP, key=lambda item:item[0])

        # THE ABOVE CODE FINDS THE OVERALL MIN/MAX LAT FOR EACH LONG
        # HOWEVER, TO FIND MAX LATERAL DIST, WE WANT TO BE CONSERVATIVE
        # AND NOT INCLUDE LEVELS THAT WRAP OVER THEMSELVES TWICE
    
        # 1) Sort all long points in descending order
        LIST_PTS = tup_list.sort(reverse=True)
        # 2) Find how many unique file pts are present
        unique_pts = len(set(TUP_LIST_TEMP, key=lambda item:item[-1]))
        # 3) If all unique, just determine dist from OVERALL Min/Max
        if len(TUP_LIST_TEMP) == unique_pts:
            lat_diff = distConv(OVERALL_MAX, OVERALL_MIN)
        # 4) Else, remove duplicates, compute distances, find max
        else:
            i = 0
            TEMP_MAX_DIST = 0
            while i <= unique_pts:
                LIST_PTS_TMP = LIST_PTS
         # 5) Remove the max from the lists, remove duplicates
                temp_max = LIST_PTS_TMP.pop(0)
                LIST_PTS.pop(0)
         # 6) Remove duplicate files, new list where files are different from temp_max file
                LIST_PTS_TMP = list(filter(lambda x: x[-1] != temp_max[-1], LIST_PTS_TMP))
         # 7) Calculate max distance
                list_pts_dist = distConv(temp_max, min(LIST_PTS_TMP, key=lambda item:item[0]))
         # 8) If greater than previous ones, update it
                if list_pts_dist > TEMP_MAX_DIST:
                    TEMP_MAX_DIST = list_pts_dist
                i += 1
         # 9) Update lat_diff
            lat_diff = TEMP_MAX_DIST
   
    # Update the min/max values (irrevlevant for max lateral distance)
    MAX_LIST.append(OVERALL_MAX)
    MIN_LIST.append(OVERALL_MIN)
    DIFF_LIST.append((LAT_DIFF, item))
    
    ####### -- FOR TESTING -- ######
    if item == -43:
        print(f"-43E MAX: {OVERALL_MAX}, MIN: {OVERALL_MIN}, DIFF: {lat_diff}") 
    
# Write the new CSV files for importing into ArcMap
with open(os.path.join(PATH,"output",'max_line.csv'), 'w', newline='') as out:
    max_out = csv.writer(out)
    max_out.writerow(["Lat","Lon"])
    for row in MAX_LIST:
        max_out.writerow(row)
        
with open(os.path.join(PATH,"output",'min_line.csv'), 'w', newline='') as out:
    min_out = csv.writer(out)
    min_out.writerow(["Lat","Lon"])
    for row in MIN_LIST:
        min_out.writerow(row)
    
with open(os.path.join(PATH, "output",'shore_diff.csv'), 'w', newline='') as out:
    diff_out = csv.writer(out)
    diff_out.writerow(["Diff, Deg","Lon"])
    for row in DIFF_LIST:
        diff_out.writerow(row)

print("End")


####################################################################
        ###      BUILD UP THE ELEVATION FILES      ###
####################################################################

# Open the CSV files in the PATH directory
# Builds THE LON and TUP LISTS for analysis
file_num2 = 0        # This labels each shoreline file
FILE_NAMES_A = []
FILE_LONS_A = []
FILE_ELEVS_A = []
FILE_NAMES_D = []
FILE_LONS_D = []
FILE_ELEVS_D = []

PATH2 = "D://Research//05_GlobalMarsShorelines//3_Results//ZachRemaps//Vertex"
for filename in os.listdir(PATH2):
    if filename.endswith(".txt") or filename.endswith(".csv"):
        print("OPENING..." + filename)
        file = open(os.path.join(PATH2,filename), newline='')
        reader = csv.reader(file)
        header = next(reader)       # The first line is the header
        
        lon_temp = []
        elev_temp = []
        for row in reader:
            # row = [OBID, NAME, FID, LAT, LON, ELEV]
            ELEV = float(row[-1])
            LON = float(row[-2])
            LAT = float(row[-3])
            lon_temp.append(LON)
            elev_temp.append(ELEV)
        if filename.find('Arabia') > 0:
            FILE_LONS_A.append(lon_temp)
            FILE_ELEVS_A.append(elev_temp)
            FILE_NAMES_A.append(filename)
        elif filename.find('Deuteronilus') > 0:
            FILE_LONS_D.append(lon_temp)
            FILE_ELEVS_D.append(elev_temp)
            FILE_NAMES_D.append(filename)
        file_num += 1
    else:
        continue

## BUILD DELTA LISTS ##
DEL_LONS = []
DEL_ELEVS = []
PATH3 = os.path.join(os.path.abspath(PATH2),"Deltas", "DiAchille2010_Deltas_Z.csv")
print(PATH3)
DEL_FILE = csv.reader(open(PATH3, newline=""))

for row in DEL_FILE:
    print(row)
    # DEL_LON_TMP = row[0]
    # DEL_ELV_TMP = row[1]
    DEL_LONS.append(float(row[0]))
    DEL_ELEVS.append(float(row[1]))

x_data1 = [x[1] for x in DIFF_LIST]
y_data1 = [x[0] for x in DIFF_LIST]
x_data2 = [x[1] for x in DIFF_LIST_WIN]
y_data2 = [x[0] for x in DIFF_LIST_WIN]

D_COLORS = ['#800000', '#9A6324', '#E6194B', '#F58231', '#FABEBE', '#FFE119']
A_COLORS = ['#4363D8', '#AAFFC3', '#F032E6', '#000000', '#000075', '#E6BEFF', '#A9A9A9', '#FFFAC8']

fig, axs = plt.subplots(3,1)
j = 0
while j < len(FILE_NAMES_D):
    axs[0].plot(FILE_LONS_D[j], FILE_ELEVS_D[j], '.', label=str(FILE_NAMES_D[j]), markersize=1, color=D_COLORS[j])
    j += 1
axs[0].plot(DEL_LONS[:], DEL_ELEVS[:], marker="s", markersize=3, mfc="#E9FFBE", mec="k", linewidth=0)
axs[0].set_xlim(-180,180)
axs[0].set_xlabel('Longitude [deg E]')
axs[0].set_ylabel('Elevation [m]')
axs[0].minorticks_on()
axs[0].grid(which='major', linestyle='-', linewidth=0.5)
axs[0].grid(which='minor', linestyle=':', linewidth=0.4)

j = 0
print("len(FILE_NAMES_A):   ", len(FILE_NAMES_A))
print("LONS_A:  ", len(FILE_LONS_A))
print("LATS_A:  ", len(FILE_ELEVS_A))
print("A_COLORS:", len(A_COLORS))
while j < len(FILE_NAMES_A):
    print(FILE_NAMES_A[j])
    axs[1].plot(FILE_LONS_A[j], FILE_ELEVS_A[j], '.', label=str(FILE_NAMES_A[j]), markersize=1, color=A_COLORS[j])
    j += 1
axs[1].plot(DEL_LONS[:], DEL_ELEVS[:], marker="s", markersize=3, mfc="#E9FFBE", mec="k", linewidth=0)
axs[1].set_xlim(-180,180)
#axs[1].set_xlabel('Longitude [deg E]')
axs[1].set_ylabel('Elevation [m]')
axs[1].minorticks_on()
axs[1].grid(which='major', linestyle='-', linewidth=0.5)
axs[1].grid(which='minor', linestyle=':', linewidth=0.4)

axs[2].plot(x_data1, y_data1, 'k')
axs[2].set_xlim(-180,180)
#axs[2].set_xlabel('Longitude [deg E]')
axs[2].set_ylabel('Max Distance [km]')
axs[2].minorticks_on()
axs[2].grid(which='major', linestyle='-', linewidth=0.5)
axs[2].grid(which='minor', linestyle=':', linewidth=0.4)

#axs[0].legend()
#axs[1].legend()
fig.tight_layout()
plt.subplots_adjust(wspace=0, hspace=0.06)

plt.show()
