# compareShorelinesWIN.py
# by Steven F. Sholes
# Updated: Mar. 14, 2020

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

PATH = "D://Research//05_GlobalMarsShorelines//1_Input//CitedShorelines//ZachRemaps//PointsOutput"
TOL = 0.25         # Tolerance for Longitude increments (in degrees)
WIN = 0          # Moving window size in multiples of TOL (e.g. 3 means 3*TOL on either side)

## Go through all inputs in the directory to find the range
LON_LIST = []        # Stores all the longitude values we are checking
TUP_LIST = []        # Stores all the tuples from all files
MAX_LIST = []        # Will store all max point tuples
MIN_LIST = []        # Will store all the min point tubles
DIFF_LIST = []       # Will store tuples (LAT DIFF, LON)
TUP_LIST_UNIQ = []   # Will store list of tuples for each unique LON
DIFF_LIST_WIN = []

#For testing
LIST_53 = []
LIST_53_min = []
LIST_53_max = []

# Open the CSV files in the PATH directory
# Builds THE LON and TUP LISTS for analysis
file_num = 0        # This labels each shoreline file
for filename in os.listdir(os.path.join(PATH,"data")):
    if filename.endswith(".txt") or filename.endswith(".csv"):
        print("OPENING..." + filename)
        file = open(os.path.join(PATH,"data",filename), newline='')
        reader = csv.reader(file)
        header = next(reader)       # The first line is the header
        
        data = []
        for row in reader:
            # row = [OBID, FID, NAME, LENGTH, LAT, LON, ELEV]
            LON = float(row[-1])
            LON_ROUND = round(LON*(1/TOL))/(1/TOL)      #Rounds to nearest TOL
            #print(LON_ROUND)
            LAT = float(row[-2])
            # if LAT > 0:                                 #Currently only looking at (+) lats
            #     #ELEV = float(row[-1])
            # 
            #     if LON_ROUND not in LON_LIST:
            #         LON_LIST.append(LON_ROUND)
            #     #TUP_LIST.append((LAT, LON_ROUND, ELEV))
            #     TUP_LIST.append((LAT, LON_ROUND))
            if LON_ROUND not in LON_LIST:
                LON_LIST.append(LON_ROUND)
            #TUP_LIST.append((LAT, LON_ROUND, ELEV))
            TUP_LIST.append((LAT, LON_ROUND, file_num))
        file_num += 1
    else:
        continue

print("Total points: ", len(TUP_LIST))

def distConv(p1, p2):
    """Takes two tuples (p1 and p2) of x,y coordiates in decimal degrees
    and converts that distance to kilometers"""
    if p1 == p2:
        return 0
    else:
        x1 = math.radians(p1[0])
        y1 = math.radians(p1[1])
        x2 = math.radians(p2[0])
        y2 = math.radians(p2[1])
        D = 3390.       # in km
        dist = D * math.acos((math.sin(y1)*math.sin(y2) + math.cos(y1)*math.cos(y2)*math.cos(x2-x1)))
        return dist

# Compares all the datapoints to find the max descrepancy for each LON
LON_LIST_UNIQ = list(set(LON_LIST))        #Removes duplicates and sorts
LON_LIST_UNIQ.sort()

#TESTING
#print(LON_LIST_UNIQ[100])

# 1) Go through each lon and find the max/min pairs
for item in LON_LIST_UNIQ:
    # Make a list of all tuples with the LON we are examining
    TUP_LIST_TEMP = [j for i, j in enumerate(TUP_LIST) if j[1] == item]
    TUP_LIST_UNIQ.append(TUP_LIST_TEMP)
    
    if len(TUP_LIST_TEMP) == 1:        #When there is only one point for that longitude
        max_lat_tup = TUP_LIST_TEMP[0]
        min_lat_tup = TUP_LIST_TEMP[0]
        lat_diff = 0
    else:                               # For all normal points
        # SET UP PERMANENT VARIABLES
        OVERALL_MAX = max(TUP_LIST_TEMP, key=lambda item:item[0])
        OVERALL_MIN = min(TUP_LIST_TEMP, key=lambda item:item[0])
        A_B_DIST_LIST = []
        
    # A - A - A  | RUN FOR GROUP A
        # Make a copy for editing that does not include the max line:
        A_TUP_LIST = list(filter(lambda z: z[-1] != OVERALL_MAX[-1], TUP_LIST_TEMP))      
        A_NUM_LIST = [OVERALL_MAX[-1]]         # For storing which lines we've checked
        A_MAX_TEMP = OVERALL_MIN          # This might break it (but can't have it as OVERALL_MAX)
        A_MIN_TEMP = OVERALL_MIN
        
        #TESTING
        if float(item) == -53.0:
            LIST_53.append([OVERALL_MAX, OVERALL_MIN, A_MAX_TEMP, A_MIN_TEMP])
        if float(item) == -53.25:
            LIST_53_max.append([OVERALL_MAX, OVERALL_MIN, A_MAX_TEMP, A_MIN_TEMP])
        if float(item) == -52.75:
            LIST_53_min.append([OVERALL_MAX, OVERALL_MIN, A_MAX_TEMP, A_MIN_TEMP])
            
        # print("*"*20)
        # print("LON:  ", item, "  TUP_LIST:  ", TUP_LIST_TEMP)
        # print("A_TUP_LIST:  ", A_TUP_LIST)
        # print("A_MAX:  ", A_MAX_TEMP, "  OVERALL MAX:  ", OVERALL_MAX)
        # print("NUM_LIST:   ", A_NUM_LIST)
        
        while len(A_TUP_LIST) > 0:
            #print("LEN:  ", len(A_TUP_LIST))
            if len(A_TUP_LIST) == 1:
                # If 1, it is the min
                A_MIN_TEMP = A_TUP_LIST[0]
                A_TUP_LIST = []
            elif len(A_TUP_LIST) == 2:
                # If 2, just find the min
                A_MIN_TEMP = min(A_TUP_LIST, key=lambda item:item[0])
                A_TUP_LIST = []
            else:
                # If >2, remove the max value and purge that line
                # If it removes all values from list, then that max is actually the min
                A_MIN_TEMP = max(A_TUP_LIST, key=lambda item:item[0])
                A_TUP_LIST = list(filter(lambda z: z[-1] != A_MIN_TEMP[-1], A_TUP_LIST))

        A_MIN = max([A_MIN_TEMP, OVERALL_MIN], key=lambda item:item[0])
        #print("A_MIN:   ", A_MIN, "   OVERALL_MIN:   ", OVERALL_MIN)
        A_B_DIST_LIST.append(distConv(OVERALL_MAX, A_MIN))
        #print("DIST LIST:  ", A_B_DIST_LIST)
        LAT_DIFF = max(A_B_DIST_LIST)
        LAT_DIFF = min([distConv(OVERALL_MAX, A_MIN), distConv(OVERALL_MAX, OVERALL_MIN)])
        #print("DIST LIST:  ", [distConv(OVERALL_MAX, A_MIN), distConv(OVERALL_MAX, OVERALL_MIN)])
        
        #TESTING
        if float(item) == -53.0:
            LIST_53.append([A_MIN])
            LIST_53.append([distConv(OVERALL_MAX, A_MIN), distConv(OVERALL_MAX, OVERALL_MIN)])
        if float(item) == -53.25:
            LIST_53_max.append([A_MIN])
            LIST_53_max.append([distConv(OVERALL_MAX, A_MIN), distConv(OVERALL_MAX, OVERALL_MIN)])
        if float(item) == -52.75:
            LIST_53_min.append([A_MIN])
            LIST_53_min.append([distConv(OVERALL_MAX, A_MIN), distConv(OVERALL_MAX, OVERALL_MIN)])

        # max_lat_tup = max(tup_list_temp, key=lambda item:item[0])
        # min_lat_tup = min(tup_list_temp, key=lambda item:item[0])
        # #lat_diff = max_lat_tup[0] - min_lat_tup[0]
        # #print(max_lat_tup, min_lat_tup)
        # lat_diff = distConv(max_lat_tup, min_lat_tup)
    
    MAX_LIST.append(OVERALL_MAX)
    MIN_LIST.append(OVERALL_MIN)
    DIFF_LIST.append((LAT_DIFF, item))
    
#print(TUP_LIST_UNIQ[100])

# print(LIST_53)
# print(LIST_53_max)
# print(LIST_53_min)


# 2) Go through it again, but now compare with window values
if WIN > 0:
    i = 0
    while i < (len(LON_LIST_UNIQ)-WIN):
        j = 0
        while j < WIN:
            #print(i, i+j, MAX_LIST[i],MAX_LIST[i+j])
            #j_maxmax_plus = distConv(MAX_LIST[i],MAX_LIST[i+j])
            #j_maxmax_min = distConv(MAX_LIST[i],MAX_LIST[i-j])
            # j_minmax_plus = distConv(MIN_LIST[i],MAX_LIST[i+j])
            # j_minmax_min = distConv(MIN_LIST[i],MAX_LIST[i-j])
            j_maxmin_plus = distConv(MAX_LIST[i],MIN_LIST[i+j])
            j_maxmin_min = distConv(MAX_LIST[i],MIN_LIST[i-j])
            #j_minmin_plus = distConv(MIN_LIST[i],MIN_LIST[i+j])
            #j_minmin_min = distConv(MIN_LIST[i],MIN_LIST[i-j])
            #temp_list_j = [j_maxmax_plus, j_maxmax_min, j_minmax_plus, j_minmax_min, \
            #                    j_maxmin_plus, j_maxmin_min, j_minmin_plus, j_minmin_min, \
            #                    DIFF_LIST[i][0]]
            #temp_list_j = [j_minmax_plus, j_minmax_min, DIFF_LIST[i][0]]
            #temp_list_j_nozero = [i for i in temp_list_j if i> 0]
            # if len(temp_list_j_nozero) == 0:
            #     temp_max_dist = 0
            # else:
            #     temp_max_dist = min(temp_list_j_nozero)
            #print(j_maxmin_plus, j_maxmin_min, DIFF_LIST[i][0])
            temp_max_dist = min(j_maxmin_plus, j_maxmin_min, DIFF_LIST[i][0])
            j += 1
        
        DIFF_LIST_WIN.append((temp_max_dist, LON_LIST_UNIQ[i]))
        i += 1
            
#print(len(MAX_LIST), len(MIN_LIST), len(LON_LIST_UNIQ))
## NEED TO CHECK THAT LAT/LON VALUES ARE VALID??


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



# j = 0
# while j < len(FILE_NAMES):
#     plt.plot(FILE_LONS[j], FILE_ELEVS[j], '.', label=str(FILE_NAMES[j]), markersize=1)
#     j += 1
# plt.xlim(-180,180)
# plt.xlabel('Longitude [deg]')
# plt.ylabel('Elevation [m]')
# plt.legend()
# plt.show()
# 
# print("End")
# 
# #Plot out the diff distribution
# #print(max(LON_LIST_UNIQ), min(LON_LIST_UNIQ))
x_data1 = [x[1] for x in DIFF_LIST]
y_data1 = [x[0] for x in DIFF_LIST]
x_data2 = [x[1] for x in DIFF_LIST_WIN]
y_data2 = [x[0] for x in DIFF_LIST_WIN]
# print(y_data2)
# plt.plot(x_data1, y_data1)
# plt.plot(x_data2, y_data2)
# plt.xlim(-180,180)
# plt.xlabel('Longitude [deg]')
# plt.ylabel('Max Lateral Distance Between Mapped Shorelines [km]')
# 
# plt.show()
#D_COLORS = ['#EFFA14', '#C1DF1B', '#94C422', '#66A92A', '#398E31', '#0C7339']
#A_COLORS = ['#E7040C', '#D00E14', '#BA181C', '#A42224', '#8E2C2C', '#783634', '#62413C', '#000000']

D_COLORS = ['#800000', '#9A6324', '#E6194B', '#F58231', '#FABEBE', '#FFE119']
A_COLORS = ['#4363D8', '#AAFFC3', '#F032E6', '#000000', '#000075', '#E6BEFF', '#A9A9A9', '#FFFAC8']

# print(FILE_ELEVS_D[1][0])
# print(FILE_ELEVS_A[1][0])

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

# j = 0
# while j < len(FILE_NAMES_A):
#     axs[3].plot(FILE_LONS_A[j], FILE_ELEVS_A[j], '.', label=str(FILE_NAMES_A[j]), markersize=0.01, color=A_COLORS[j])
#     j += 1
# j = 0
# while j < len(FILE_NAMES_D):
#     axs[3].plot(FILE_LONS_D[j], FILE_ELEVS_D[j], '.', label=str(FILE_NAMES_D[j]), markersize=0.01, color=D_COLORS[j])
#     j += 1
# axs[3].grid(True)
# axs[3].set_xlim(-180,180)

#axs[0].legend()
#axs[1].legend()
fig.tight_layout()
plt.subplots_adjust(wspace=0, hspace=0.06)

plt.show()