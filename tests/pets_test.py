import pandas as pd
import ast
df = pd.read_csv('apartments.csv')
df['petsArray'] = df['petsArray'].apply(ast.literal_eval)
def transform_pets(val):
    return val if val else None
df['pets'] = df['petsArray'].apply(transform_pets)
print(df['pets'])