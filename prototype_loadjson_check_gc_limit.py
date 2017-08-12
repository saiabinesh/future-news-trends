#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!python2
import json, codecs, sys
import sqlite3
import time
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from datetime import datetime
from gensim import corpora, models
from nltk import ngrams
from nltk.stem.porter import *
stemmer = PorterStemmer()

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
conn = sqlite3.connect('example2.db')

def returnStories():
    global startDate
    global endDate
    global gc

    
    c = conn.cursor()

    sql = ''' select text, features from news where date between date(?) and date(?) limit ? '''

    c.execute(sql,[startDate,endDate, gc])
    return c


#def returnStories(location):
#    f= open(location)
#    for line in f:
#        a = json.loads(line)
#        if a['media-type'] != "News":
#            continue
#        yield a
      
#    f.close()




def returnNgrams(sentence,n=3):
    words = [" ".join(w).strip() for w in ngrams(word_tokenize(sentence),n) if not set(w).intersection(stopwords)]
    return words


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
            
     
    #words = returnNgrams(words,n=3)
    words = filter(lambda x:  not x.lower() in stopwords,words)
    return words
    
    
def createTopics(words):
    #step 1

    #print (type(words))
    #exit()
   
    
    dictionary = corpora.Dictionary(words)
    dictionary.save('dictionary.dict')

    global global_dict
    global_dict = dictionary

    #step 2
    #convert to bag of words
    corpus = map (dictionary.doc2bow, words)
    corpora.MmCorpus.serialize('corpus.mm', corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

   
       
    #lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=notopics)

    lda = models.LdaMulticore(corpus_tfidf, id2word=dictionary, num_topics=notopics, workers=4)
    corpus_lda = lda[corpus_tfidf]

    global global_lda
    global_lda = lda   

    #step 3
    #save topic models
    #These are models that you use to make topic inferences about documents
    lda.save("model_"+str(i)+"_"+str(notopics)+"topics.lda") 
    pickle.dump(corpus_lda, open("corpus_lda.pck","wb"))                
    pickle.dump(tfidf, open("tfidf.pck","wb"))
   

    #can add in other types of topic modelling

    
    print ("done")


def sortFunction(d):
    global globalCount
    global gc

    globalCount+=1

    if gc <= globalCount:
        return False
    
    
    key ="published"
    if key not in d:
        return False

    dictDate =d[key]
    #remove time portion
    dictDate = dictDate.split("T")[0]
    dictDate = datetime.strptime(dictDate, pattern)

    if dictDate >= startDate and dictDate <= endDate:
        return True
    

def updateDictionary(time_series, docdate, topicno, iteration):

    if not iteration in time_series:
        d = {}
        tn = {topicno:1}
        d[docdate]= tn
        time_series[iteration] = d
        return time_series

    ts = time_series[iteration]
    tn = {topicno:0}
    if docdate in ts:
        tn = ts[docdate]
        if not topicno in tn:
            tn[topicno] = 0
        
    tn[topicno]+=1
    ts[docdate] = tn
    time_series[iteration] = ts
    return time_series
    
def inferTopic(docs, iteration):
    global global_lda
    global global_dict
    global time_series

    #global_lda = pickle.load(open("corpus_lda.pck")) 
    #global_dict = pickle.load(open('dictionary.dict'))
    for doc in docs:
        bw = global_dict.doc2bow(doc["content"].split())
        
        
        lda_vector = global_lda[bw]
        if not lda_vector:
            continue
        a= max([l[1] for l in lda_vector])
        docdate = doc["published"].split("T")[0]
        for i in lda_vector:
            if not i[1]==a:
                continue
            topicno = i[0]
            time_series = updateDictionary(time_series, docdate, topicno, iteration)
            break
            
    print (time_series)
    print ("")
    exit()
    



if __name__ == "__main__":

    pattern = "%Y-%m-%d"

    #startDate = sys.argv[2]
    startDate = "2015-09-01"
    startDate =  datetime.strptime(startDate, pattern)

    #endDate = sys.argv[3]
    endDate = "2015-09-02"
    endDate =  datetime.strptime(endDate, pattern)
    
    #notopics = sys.argv[4]
    notopics = 600
    
    location ="sample-1M.jsonl"
    #location =  sys.argv[1]
    if not os.path.isfile(location):
        print ("File %s does not exist") % (location)
        exit()

    stopwords = set(stopwords.words('english'))
    iteration =1

    gc = 100000

    #for gc in range(100,100000, 500):
    start_time = time.time()
    results = returnStories()
    #filter(sortFunction,returnStories(location))
    print ("sorted")
    end_time = time.time()
    print("--- %s seconds --- %d\n" % (end_time - start_time, gc))
    exit()

    #build topic models
    words = map(filterWords,results)
    print ("pre-processed")
   
    createTopics(words)

    #infer topic one story
    #s= returnStories(location)
    end_time = time.time()
    print("--- %s seconds --- %d\n" % (end_time - start_time, gc))
    
    conn.close()
    exit()
    inferTopic(s,iteration)
   
        
        #end_time = time.time()
        #print("--- %s seconds --- %d\n" % (end_time - start_time, gc))
        #globalCount = 0
    print ("done")


