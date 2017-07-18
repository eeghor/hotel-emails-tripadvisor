"""
a helper to create a data frame from the Hotel named tuples stored in text files
"""

from collections import namedtuple
import pandas as pd
import os

# it's assumed that all the files we want to read are in the data directory and have names starting from hotels_
files = ["data/" + f for f in os.listdir("data") if "hotels_" in f]
print("found {} hotel files".format(len(files)))

# specify what's this Hotel namedtuple
Hotel = namedtuple("Hotel", "tradv_id name address website email")

all_tuples = []

for file in files:
	with open(file, "r") as f:
		all_tuples.extend([eval(line.strip()) for line in  f.readlines()])

df = pd.DataFrame.from_records(all_tuples, columns=Hotel._fields)
df.drop_duplicates("tradv_id", inplace=True)

print("created a data frame containing {} hotels".format(len(df)))

# save this data frame to csv
df.to_csv("data/australian_hotels.csv", index=False, sep="\t")
