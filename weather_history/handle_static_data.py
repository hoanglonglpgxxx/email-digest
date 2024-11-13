import pandas as pd
import numpy as np

# Read data file, skip first 20 text lines and parse the 'DATE' column as datetime

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


def get_temperature(station, date):
    """
        Read data file from the specified weather station and date, and return the temperature.

    :param station: station ID
    :type station: str
    :param date: date in 'YYYY-MM-DD' format
    :type date: str
    :return: temperature in celsius
    :rtype: float
    """
    file = f'data-small/TG_STAID{str(station).zfill(6)}.txt'
    df = pd.read_csv(file, skiprows=20, parse_dates=['    DATE'])

    # Get temp of a cell
    temperature = df.loc[df['    DATE'] == date]['   TG'].squeeze() / 10

    return temperature

def get_word_definition(word):
    """

    :param word: word
    :type word: str
    :return: definition of word
    :rtype: str
    """
    df = pd.read_csv('dictionary.csv')
    if df.empty:
        return 'No Meaning'
    definition = df.loc[df['word'] == word]['definition']
    print(df.loc[df['word'] == word])
    return definition.squeeze() if not definition.empty else 'No Meaning'
