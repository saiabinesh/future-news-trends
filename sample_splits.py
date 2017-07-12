#getting the list of dictionaries initialized for just the split
import re, pickle

splits = pickle.load(open("splits.pck","rb"))

#print(splits)
print(len(splits))