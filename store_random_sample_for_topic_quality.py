import sys
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("logfile.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()

from datetime import datetime, timedelta
print("\nExperiment time: ",datetime.now())
print("Storing a random sample on to disk for assessing topic model quality later.")

import json, codecs, sqlite3
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
import random
random.seed(1000)

global location
global startDate
global endDate
global pattern
global notopics
global stopwords
global regPattern
global globalCount
global gc
global global_lda
global global_dict

regPattern = "[^A-Za-z\s-]"
regPattern = re.compile(regPattern)

conn = sqlite3.connect('example2.db')

def returnStories():
    global startDate
    global endDate
    global gc
  
    c = conn.cursor()

    sql = ''' select text, features from news order by random() limit 400  ''' 
    c.execute(sql)
    return c
    
def filterWords(d):
    #get texts and filter stopwords
    #words = regPattern.sub(' ',d['content'])
    words = d[1]
    return words.split()

    
    words = word_tokenize(words)
    pos_tag = nltk.pos_tag(words)
    words = []
    for w in pos_tag:
        if w[0] != regPattern.sub(' ',w[0]):
            continue
        if w[0] =="javascript" or w[0]=="http":
            continue

        #if w[0][-1]=="s" and w[0][-1]!="s" and len(w[0])>4:
        #    words.append(w[0][0:-1].lower())
        #    continue
        
        if "N" in w[1][0] and len(w[0])>3 and w[1]!="NNP":
            words.append(w[0].lower())
    words = [stemmer.stem(plural) for plural in words]
            
     
    
    words = filter(lambda x:  not x.lower() in stopwords,words)
    return words

results = returnStories()
test_corpus = map(filterWords,results)
pickle.dump(test_corpus, open("test_sample.pck","wb"))
print(type(test_corpus))

conn.close()
exit()    
