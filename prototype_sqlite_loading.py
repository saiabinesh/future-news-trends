import json, codecs, sys, sqlite3
import os.path, string
import re, pickle, datetime

topic_frequency_dicts = pickle.load(open("topic_frequency_dicts1.pck","rb"))
list_of_lists = []
for dict in topic_frequency_dicts:
    dict['Date'] = str(dict['Date'])
    # print(dict["Date"])
    # exit()
    temp_tuple = tuple(dict.values())
    list_of_lists.append(temp_tuple)

conn = sqlite3.connect('db\models.db')
c = conn.cursor()
print(list_of_lists[1])
c.executemany('INSERT INTO Test VALUES(?,?,?,?,?,?)', list_of_lists)
conn.commit()
conn.close()