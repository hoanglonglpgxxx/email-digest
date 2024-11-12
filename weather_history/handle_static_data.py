import pandas as pd
import numpy as np

# Read data file, skip first 20 text lines and parse the 'DATE' column as datetime
df = pd.read_csv('data-small/TG_STAID000001.txt', skiprows=20, parse_dates=['    DATE'])

# Show certain columns
# print(df.columns) # return cols of data frame
# print(df['   TG']) # return Series object
# print(df[['   TG', '    DATE']]) # return DataFrame object
# print(df['   TG'].mean()) # mean() is method of pandas, calculate avg val of that col
# print(df['   TG'].max()) # max val in col, beside of min()
# print(df.loc[df['   TG'] != -9999]) # df.loc[condition], use to filter values

# Get certain cells
# print(df.loc[df['    DATE'] == '1860-01-05']['   TG'].squeeze())
# print(df.loc[3, '    DATE']) #Get value of date col at row 3

# Calculate a new col out of existing col
# df['TG0'] = df['   TG'].mask(df['   TG']==-9999, np.nan) # Replace all -9999 with nan
# df['TG'] = df['TG0'] / 10
# print(df)


def handle_data(station):
    """
    Read data file from station param
    :param station:
    :return: temperature
    """
    print(f'data-small/TG_STAID{station.zfill(6)}.txt')
