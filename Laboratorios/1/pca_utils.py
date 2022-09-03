import string
import pandas as pd

def load_df(name: string):
   return pd.read_csv(name)

def preprocess_df(df):
  print(df)

preprocess_df(load_df('titanic.csv'))