# compareMarsLevelsData.py
# By Steven F. Sholes (sfsholes@uw.edu)
# Created for Sholes et al. 2020 submitted to JGR: Planets

# This calculates and plots the lateral offset and elevations between
#  different maps of the hypothetical Arabia and Deuteronilus shorelines
#  on Mars.

# Import dependencies
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import re

# PATH: main directory everything else is stored in
PATH = os.path.dirname(os.path.realpath(__file__))
# OFFSET_PATH: location within PATH where lateral offset data is stored
OFFSET_PATH = os.path.join(PATH,"Offset_CSV_files")
# ELEV_PATH: location within PATH where elevation data is stored
ELEV_PATH = os.path.join(PATH,"Levels_CSV_files")
# DELTA_PATH: file location within ELEV_PATH where delta elevation data is stored
DELTA_PATH = os.path.join(PATH,"Delta_CSV_files", "DiAchille2010_Deltas_Z.csv")

def openData(path):
    """Opens up the .csv files of the lateral offset data in the given path and
    adds them to a pandas dataframe
    input path: str
    return combined_df: list of pandas dataframes"""

    combined_df = []
    #### --- OPEN UP THE DATA --- ###
    # Open the CSV files in the PATH directory
    file_num = 0        # This labels each shoreline file
    for root, dirs, files in os.walk(path):
        for file in files:
            # FINDS ALL TXT AND CSV FILES IN DIRECTORY TO OPEN
            # Sometimes ArcMap outputs incorrectly
            if file.endswith(".txt") or file.endswith(".csv"):
                print("Opening offset data from..." + file)
                new_df = pd.read_csv(os.path.join(root, file))
                combined_df.append(new_df)
            else:
                continue

    for dataset in combined_df:
        # This is needed to ensure all points are at nearest 1/4 line of longitude
        dataset['Lon'] = dataset['Lon'].apply(lambda x: round(x*(1/0.25))/(1/0.25))
        dataset['Lon'] = dataset['Lon'].apply(lambda x: 180.0 if x == -180.0 else x)
        #print(dataset.head())

    return combined_df

def findLen(data, method="min"):
    """Finds the minimum/mean/maximum geodesic length between different datasets
    for each longitude. Defaults to min to be conservative.

    input data: list of pandas dataframes
    input method: a str of either "min," "mean," or "max"
    return result_df: a pandas dataframe"""

    #Concatenating all dataframes makes it much easier to work on
    full_df = pd.concat(data)

    #Check which method to use and apply it. A little leeway in choices.
    if method.lower() in ["min", "minimum"]:
        result_df = full_df.groupby('Lon')['Geodesic Length [km]'].min().reset_index()
    elif method.lower() in ["mean", "average"]:
        result_df = full_df.groupby('Lon')['Geodesic Length [km]'].mean().reset_index()
    elif method.lower() in ["max", "maximum"]:
        result_df = full_df.groupby('Lon')['Geodesic Length [km]'].max().reset_index()
    else:
        print("Choose either 'min', 'mean', or 'max'")
        pass

    return result_df

def grabElevation(path):
    """Finds the elevation data in the path and places it into a pandas dataframe
    input path: str showing location of csv elevation files
    return level_list: list of 2 dictonaries with label and pandas dataframe"""

    #Going to output a list of two lists of pandas dataframes
    #level_list[0] are the Arabia level data
    #level_list[1] are the Deuteronilus level data
    level_list = [{},{}]
    for root, dirs, files in os.walk(path):
        for file in files:
            # Sometimes ArcMap exports as .csv or .txt
            if file.endswith(".txt") or file.endswith(".csv"):
                # Perron et al. 2007 data is a subset of the Carr and Head (2003) data
                if file.find('2007') > 0:
                    continue
                print("Reading elevations from..." + file)
                elev_temp_df = pd.read_csv(os.path.join(root, file))
                # Need to convert column key names as they can be irregular in structure
                elev_temp_df.columns = elev_temp_df.columns.str.lower().str.capitalize()
                # Extract the citation from the filename using regex
                # e.g., finds _Parker1993_ and extracts out Parker1993 for the label
                # This is a holdover from previous version. Should fix to pull from directory label now
                head_label = re.search(r'([A-Za-z]+[0-9]+)_', file).group(1)
                #print('Header...', head_label
                # This creates a new column with the new label and places the elevation data there
                if file.find('Arabia') > 0:
                    level_list[0][head_label] = elev_temp_df
                elif file.find('Deuteronilus') > 0:
                    level_list[1][head_label] = elev_temp_df
                else:
                    continue
            else:
                continue
    #print(level_list)
    return level_list

def plotOffsets(elev_dataset, offset_data):
    """Plots the offsets between the different methodologies
    input elev_dataset: pandas dataframe of elevation data
    input offset_data: list of pandas dataframes with lateral offset data
                       offset[0] : list of df for DEUTERONILUS
                       offset[1] : list of df for ARABIA
    returns nothing but does plot the figure for the paper

    NOTE: Figure 1 in the paper uses densified data to make the plots easier to
    read (i.e., taking the shapefile polylines and adding vertices at 1 km increments)
    But the data in Table 1 uses the vertices that were used in the digitization
    process (or author provided data files)."""

    # Lists of colors to be consistent with ArcMap plot (Fig. 1a)
    # D_COLORS for Deuteronilus Level, A_COLORS for Arabia Level, O_Colors for offset lines
    D_COLORS = ['#800000', '#9A6324', '#E6194B', '#F58231', '#FABEBE', '#FFE119']
    A_COLORS = ['#4363D8', '#AAFFC3', '#F032E6', '#000000', '#000075', '#E6BEFF', '#A9A9A9', '#FFFAC8']
    O_COLORS = ['#000000', '#888888'] # '#CCCCCC' is for backup
    O_COLORS2 = ['#000000', '#888888']

    ### --- OPEN DELTA DATA --- ###
    delta_df = pd.read_csv(DELTA_PATH)

    D_COLORS = ['#7E0000', '#A76921', '#73E1DF', '#FEC4FF', '#FAC0C0', '#000000', '#5EEE11']
    A_COLORS = ['#E60000','#0081C8', '#A8FFC2', '#FFAA00', '#FFFF00', '#01017F', '#CCCCCC', '#9B3AC5']

    fig, axs = plt.subplots(4,1)
    ### --- PLOT DEUTERONILUS ELEVATIONS --- ###
    print(elev_dataset[1].keys())
    for key, df in zip(elev_dataset[1].keys(), elev_dataset[1].values()):
        # using pop below works but should be edited later if using the colors again
        axs[0].plot(df['Lon'], df['Elevation [m]'], '.', label=key, markersize=0.8, color=D_COLORS.pop(0))
    axs[0].plot(delta_df['Lon'], delta_df['Elevation [m]'], marker="s", markersize=3, mfc="#E9FFBE", mec="k", linewidth=0)
    axs[0].set_xlim(-180,180)
    axs[0].set_xlabel('Longitude [deg E]')
    #axs[0].set_ylabel('Elevation [m]')
    axs[0].minorticks_on()
    axs[0].grid(which='major', linestyle='-', linewidth=0.5)
    axs[0].grid(which='minor', linestyle=':', linewidth=0.4)

    ### --- PLOT ARABIA ELEVATIONS --- ###
    for key, df in zip(elev_dataset[0].keys(), elev_dataset[0].values()):
        # using pop below works but should be edited later if using the colors again
        axs[1].plot(df['Lon'], df['Elevation [m]'], '.', label=key, markersize=0.8, color=A_COLORS.pop(0))
    axs[1].plot(delta_df['Lon'], delta_df['Elevation [m]'], marker="s", markersize=3, mfc="#E9FFBE", mec="k", linewidth=0)
    axs[1].set_xlim(-180,180)
    #axs[1].set_xlabel('Longitude [deg E]')
    #axs[1].set_ylabel('Elevation [m]')
    axs[1].minorticks_on()
    axs[1].grid(which='major', linestyle='-', linewidth=0.5)
    axs[1].grid(which='minor', linestyle=':', linewidth=0.4)

    ### --- PLOT DEUTERONILIUS OFFSETS --- ###
    for data in offset_data[0]:
        axs[2].plot(data['Lon'], data['Geodesic Length [km]'], color=O_COLORS2.pop(0))
    axs[2].set_xlim(-180,180)
    axs[2].set_ylim(0,1400)
    #axs[2].set_xlabel('Longitude [deg E]')
    #axs[2].set_ylabel('Min Offset [km]')
    axs[2].minorticks_on()
    axs[2].grid(which='major', linestyle='-', linewidth=0.5)
    axs[2].grid(which='minor', linestyle=':', linewidth=0.4)

    ### --- PLOT ARABIA OFFSETS --- ###
    for data in offset_data[1]:
        axs[3].plot(data['Lon'], data['Geodesic Length [km]'], color=O_COLORS.pop(0))
    axs[3].set_xlim(-180,180)
    axs[3].set_ylim(0,1400)
    #axs[3].set_xlabel('Longitude [deg E]')
    #axs[3].set_ylabel('Min Offset [km]')
    axs[3].minorticks_on()
    axs[3].grid(which='major', linestyle='-', linewidth=0.5)
    axs[3].grid(which='minor', linestyle=':', linewidth=0.4)

    #axs[0].legend()
    #axs[1].legend()
    fig.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0.06)

    plt.show()

def calculateStats(arabia, deuteronilus):
    """Determines the mean/standard deviation for both levels"""
        # I'm not sure why but the f strings don't like the pd df keys in line
    A_mean = arabia.mean()['Geodesic Length [km]']
    A_std = arabia.std()['Geodesic Length [km]']
    A_max = arabia.loc[[arabia['Geodesic Length [km]'].idxmax()]]
    D_mean = deuteronilus.mean()['Geodesic Length [km]']
    D_std = deuteronilus.std()['Geodesic Length [km]']
    D_max = deuteronilus.loc[[deuteronilus['Geodesic Length [km]'].idxmax()]]

    print(
        'Arabia Stats: \n'
        f'Min offset mean: {A_mean:.1f} km \n'
        f'Min offset std:  {A_std:.1f} km \n\n'
        'Deuteronilus Stats: \n'
        f'Min offset mean: {D_mean:.1f} km \n'
        f'Min offset std:  {D_std:.1f} km \n'
        )
    print("Arabia Max Value: \n", A_max)
    print("Dueteronilus Max: \n", D_max)

def run():
    """Plots the data and prints the stats"""
    ### --- CALCULATE ARABIA OFFSETS --- ###
    A_offset_data = openData(os.path.join(OFFSET_PATH, 'Arabia'))
    A_min_offset = findLen(A_offset_data, method="min")
    A_max_offset = findLen(A_offset_data, method="max")
    ### --- CALCULATE DEUTERONILUS OFFSETS --- ###
    D_offset_data = openData(os.path.join(OFFSET_PATH, 'Deuteronilus'))
    D_min_offset = findLen(D_offset_data, method="min")
    D_max_offset = findLen(D_offset_data, method="max")

    elev_df = grabElevation(ELEV_PATH)

    # I've plotted them in reverse so the main one ("min") is plotted on top
    plotOffsets(elev_df, [[D_min_offset],[A_min_offset]])
    calculateStats(A_min_offset, D_min_offset)

if __name__ == '__main__':
    run()
