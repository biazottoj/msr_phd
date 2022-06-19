import pandas as pd

with open('data.csv','r') as file:
    df = pd.read_csv(file)

filtered = df.groupby(['project']).mean()

print(filtered)