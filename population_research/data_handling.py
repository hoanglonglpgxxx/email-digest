import pandas as pd

def handle_data(key):
    df = pd.read_csv('happy.csv')

    print(df[key].squeeze(), type(df[key].squeeze()))
    return df[key]
