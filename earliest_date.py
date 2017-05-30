import json, codecs, sys
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from datetime import datetime
from gensim import corpora, models

global location
global startDate
global endDate
global pattern
global notopics
global stopwords
global regPattern
global date_list
global early_date_set
global assumed_earliest_date
global train_startdates
global train_enddates
global test_startdates
global test_enddates

train_startdates = []
train_enddates=[]
test_startdates=[]
test_enddates=[]
assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
early_date_set = set()
regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)
date_list = []

def returnStories(location):
    f = codecs.open(location,'r',"utf-8")
    for line in f:
        a = json.loads(line)
        yield a
      
    f.close()

def get_dates(d):
    global date_list
    global early_date_set
    global assumed_earliest_date
    
    key ="published" #published the json line having the date
    if key not in d:
        return False
    #extracting string date from the dictionary of the current news item
    current_date =d[key] 
    #remove time portion
    current_date = current_date.split("T")[0]
    pattern = "%Y-%m-%d"
    current_date = datetime.strptime(current_date, pattern)
    #appending the date of the current item onto a global date_list
    if current_date<assumed_earliest_date:
        early_date_set.add(current_date)
    date_list.append(current_date)
    
        
    
   
if __name__ == "__main__":
    location ="sample-1M.jsonl"
    #location =  sys.argv[1]
    if not os.path.isfile(location):
        print ("File %s does not exist" % (location))
        exit()

    #map(get_dates,returnStories(location))
    #For every item(news story or blog) in the data, getting it's date and appending to the global date lista
    for item in returnStories(location):
        get_dates(item)
    #To get a unique list of all different dates before 1st sep 2015
    #for date in early_date_set:
        #print (str(date))
        
    #Printing the earliest date
    print("Earliest date")
    print (min(early_date_set))
    print("Unique dates before 1st Sep 2015")
    print(sum(i < assumed_earliest_date for i in early_date_set))
    print("Count of news items before 1st Sep 2015")
    print(sum(i < assumed_earliest_date for i in date_list))
    
    offsets = range(0,11)
    random.shuffle(offsets)
    offsets =offsets[0:9]
    
    global startdate
    for r in range(1,9):
        

