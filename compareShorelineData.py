import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import re

PATH = "D://Research//05_GlobalMarsShorelines//3_Results"
OFFSET_PATH = os.path.join(os.path.abspath(PATH),"0_Offsets", "Data")
ELEV_PATH = os.path.join(os.path.abspath(PATH),"ZachRemaps", "Vertex")
DELTA_PATH = os.path.join(os.path.abspath(ELEV_PATH),"Deltas", "DiAchille2010_Deltas_Z.csv")

def openData(path):
    """Opens up the .csv files in the given path and adds them to a
    pandas dataframe
    input path: str
    return combined_df: list of pandas dataframes"""

    combined_df = []
    #### --- OPEN UP THE DATA --- ###
    # Open the CSV files in the PATH directory
    file_num = 0        # This labels each shoreline file
    for filename in os.listdir(path):
        # FINDS ALL TXT AND CSV FILES IN DIRECTORY TO OPEN
        # Sometimes ArcMap outputs incorrectly
        if filename.endswith(".txt") or filename.endswith(".csv"):
            print("Opening offset data from..." + filename)
            new_df = pd.read_csv(os.path.join(path,filename))
            combined_df.append(new_df)
        else:
            continue

    for dataset in combined_df:
        # This is needed to ensure all points are at nearest 1/4 line of longitude
        dataset['Lon'] = dataset['Lon'].apply(lambda x: round(x*(1/0.25))/(1/0.25))
        dataset['Lon'] = dataset['Lon'].apply(lambda x: 180.0 if x == -180.0 else x)
        #print(dataset.head())

    return combined_df

def meanLon(dataset):
    """Find the mean geodesic length for each line of longitude within a given
    dataset (e.g., where multiple measurements are made at each lon).
    input dataset: pandas dataframe
    return mean_dataset: pandas dataframe"""
    updated_list = []
    for database in dataset:
        #print(database.head())
        new_df = database.groupby('Lon').mean()
        updated_list.append(new_df)

    return updated_list

def findMinLen(data):
    """Finds the minimum geodesic length between different datasets for each long
    input data: list of pandas dataframes
    return min_df: single pandas dataframe with geodesic lengths for each unique lon"""

    full_df = pd.concat(data)
    min_df = full_df.groupby('Lon')['LENGTH_GEO'].min().reset_index()

    return min_df

def grabElevation(path):
    """Finds the elevation data in the path and places it into a pandas dataframe"""

    #Going to output a list of two lists of pandas dataframes
    #level_list[0] are the Arabia level data
    #level_list[1] are the Deuteronilus level data
    level_list = [{},{}]

    for filename in os.listdir(path):
        # Sometimes ArcMap exports as .csv or .txt
        if filename.endswith(".txt") or filename.endswith(".csv"):
            print("Reading elevations from..." + filename)

            elev_temp_df = pd.read_csv(os.path.join(path,filename))
            elev_temp_df.columns = elev_temp_df.columns.str.lower().str.capitalize()
            print(filename)
            head_label = re.search(r'_([A-Za-z]+[0-9]+)_', filename).group(1)
            print('Header...', head_label)
            if filename.find('Arabia') > 0:
                level_list[0][head_label] = elev_temp_df
            elif filename.find('Deuteronilus') > 0:
                level_list[1][head_label] = elev_temp_df
            else:
                continue
        else:
            continue
    print(level_list)
    return level_list

def plotOffsets(elev_dataset, offset_data):
    """Plots the offsets between the different methodologies"""

    D_COLORS = ['#800000', '#9A6324', '#E6194B', '#F58231', '#FABEBE', '#FFE119']
    A_COLORS = ['#4363D8', '#AAFFC3', '#F032E6', '#000000', '#000075', '#E6BEFF', '#A9A9A9', '#FFFAC8']

    fig, axs = plt.subplots(3,1)
    ### --- PLOT DEUTERONILUS ELEVATIONS --- ###
    for key, df in zip(elev_dataset[1].keys(), elev_dataset[1].values()):
        print('key...', key)
        print(df)
        # using pop below works but should be edited later if using the colors again
        axs[0].plot(df['Lon'], df['Elev'], '.', label=key, markersize=0.8, color=D_COLORS.pop(0))
    axs[0].set_xlim(-180,180)
    axs[0].set_xlabel('Longitude [deg E]')
    axs[0].set_ylabel('Elevation [m]')
    axs[0].minorticks_on()
    axs[0].grid(which='major', linestyle='-', linewidth=0.5)
    axs[0].grid(which='minor', linestyle=':', linewidth=0.4)

    ### --- PLOT ARABIA ELEVATIONS --- ###
    for key, df in zip(elev_dataset[0].keys(), elev_dataset[0].values()):
        # using pop below works but should be edited later if using the colors again
        axs[1].plot(df['Lon'], df['Elev'], '.', label=key, markersize=0.8, color=A_COLORS.pop(0))
    axs[1].set_xlim(-180,180)
    #axs[1].set_xlabel('Longitude [deg E]')
    axs[1].set_ylabel('Elevation [m]')
    axs[1].minorticks_on()
    axs[1].grid(which='major', linestyle='-', linewidth=0.5)
    axs[1].grid(which='minor', linestyle=':', linewidth=0.4)

    ### --- PLOT ARABIA OFFSETS --- ###
    axs[2].plot(offset_data['Lon'], offset_data['LENGTH_GEO'], 'k')
    axs[2].set_xlim(-180,180)
    axs[2].set_ylim(0,2600)
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


shoreline_data = openData(PATH)
offset_df = findMinLen(meanLon(openData(OFFSET_PATH)))
elev_df = grabElevation(ELEV_PATH)

plotOffsets(elev_df, offset_df)
