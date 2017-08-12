#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!python2
#Below class displays output in console as well as logging it in a logfile.log file
import sys
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("/home/sai/project/data/logfile.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()

import json, codecs, sys
import sqlite3
import time, random
from time import time
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from datetime import datetime, timedelta
from gensim import corpora, models
from nltk import ngrams
from nltk.stem.porter import *
stemmer = PorterStemmer()

import json, codecs, sys, sqlite3
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from gensim import corpora, models
import random
random.seed(1000)
from time import time

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

gc = 0
globalCount = 0

global time_series
time_series ={}

global conn
conn = sqlite3.connect('/home/sai/project/data/example2.db')

def returnStories():
    global startDate
    global endDate
    global gc

    
    c = conn.cursor()

    sql = ''' select text, features from news where date between date(?) and date(?)  '''

    c.execute(sql,[startDate,endDate])
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
    
    
def createTopics(words):
    
    dictionary = corpora.Dictionary(words)
    dictionary.save("dictionary_"+str(i)+"_"+str(notopics)+"topics.dict")

    global global_dict
    global_dict = dictionary

    #step 2
    #convert to bag of words
    corpus = map (dictionary.doc2bow, words)
    corpora.MmCorpus.serialize("corpus_"+str(i)+"_"+str(notopics)+"topics.mm", corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    lda = models.LdaMulticore(corpus_tfidf, id2word=dictionary, num_topics=notopics, workers=4)
    # The following line of code gets topic probability distribution for a document
    # corpus_lda = lda[corpus_tfidf]

    global global_lda
    global_lda = lda   

    #step 3
    #save topic models
    #These are models that you use to make topic inferences about documents
    lda.save("model_"+str(i)+"_"+str(notopics)+"topics.lda") 
    # pickle.dump(corpus_lda, open("corpus_lda.pck","wb"))                
    pickle.dump(tfidf, open("tfidf.pck","wb"))
    print ("done")



if __name__ == "__main__":

    pattern = "%Y-%m-%d"
    print("\nExperiment time: ",datetime.now())
    print("Objective: Getting topic models with different number of topics. Trying 200 and 300 topics now.")
  
    # location ="/project/data/signalmedia-1m.jsonl"
    # #location =  sys.argv[1]
    # if not os.path.isfile(location):
        # print ("File %s does not exist") % (location)
        # exit()
    assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
    random.seed(1000)
    offsets = list(range(11))
    random.shuffle(offsets)
    offsets =offsets[0:9]
    # print(offsets)
    f1st_sep = assumed_earliest_date #fst_sep is the first of september 2015
    splits=[]
    
    global startdate
    for r in range(0,9):
        current_line={'Offset': offsets[r], 'Train start date': f1st_sep+timedelta(days=offsets[r]), 'Train end date': f1st_sep+timedelta(days=offsets[r]+8), 'Test start date': f1st_sep+timedelta(days=offsets[r]+9), 'Test end date': f1st_sep+timedelta(days=offsets[r]+17)}
        splits.append(current_line)
    
    stopwords = set(stopwords.words('english'))
    
    notopics = 700
    #start_time = time.time()
    i=1
    print("Topic modelling phase: Number of topics = ",notopics)
    
    #First model already built. So using continue to skip to the next item in the split
    for dict in splits:
        if i==1:
            i=i+1
            continue
        else:
            startDate = dict['Train start date']
            endDate = dict['Train end date']
            #build topic models
            results = returnStories()
            print ("Extracted documents- Iteration",(i))
            test_corpus = map(filterWords,results)
            print ("pre-processed")
            print(datetime.now().strftime('%H:%M:%S'))
            createTopics(test_corpus)
            print(datetime.now().strftime('%H:%M:%S'))
            print("------")
            i=i+1

    
    conn.close()
    exit()
    inferTopic(s,iteration)
   
        
        #end_time = time.time()
        #print("--- %s seconds --- %d\n" % (end_time - start_time, gc))
        #globalCount = 0
    print ("done")


