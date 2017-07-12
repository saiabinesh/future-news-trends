#Below class displays output in console as well as logging it in a logfile.log file
import sys
# orig_stdout = sys.stdout
# f = open('logfile.log', 'a')
# sys.stdout = f

from datetime import datetime, timedelta
print("\nExperiment time: ",datetime.now())
print("Testing topic inference frequencies in sqlite table against sample of 25 documents for all splits by just eyeballing.")

import json, codecs, sys, sqlite3
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from gensim import corpora, models
import random
random.seed(1000)

global location
global startDate
global endDate
global pattern
global notopics
global stopwords
global regPattern
global i
global splits
global topic_frequency_dicts

#Creating a list of dates in the 1 month range to be iterated over later
date_list = []
earliest_date =datetime(2015,9,1)
latest_date =datetime(2015,9,30)
date_list_1= [date_list.append(datetime(2015,9,day)) for day in range(1,31) ]

assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
early_date_set = set()
regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)
splits=[]
conn = sqlite3.connect('db\models.db')
c = conn.cursor()

for i in range(1,10):
    topic_frequency_dicts = pickle.load(open("topic_frequency_dicts_21Jun_25docs_"+str(i)+".pck","rb"))
    list_of_lists = []
    print("Iteration: ",i)
    print("size of topic_frequency_dicts: ",len(topic_frequency_dicts))
    for dict in topic_frequency_dicts:
        dict['Date'] = str(dict['Date'])
        # print(dict["Date"])
        # exit()
        temp_tuple = tuple(dict.values())
        list_of_lists.append(temp_tuple) 
    c.executemany('INSERT INTO Test_25_6 VALUES(?,?,?,?,?,?)', list_of_lists)
        
conn.commit()
conn.close()