#Below class displays output in console as well as logging it in a logfile.log file
import sys

orig_stdout = sys.stdout
f = open('logfile.log', 'a')
sys.stdout = f

from datetime import datetime, timedelta
print("\nExperiment time: ",datetime.now())
print("Objective: Trying to understand the difference in time between the time taken by the virtual machine and this machine by running and comparing the time taken to print a model.")
# increase the eta parameter and check the results.\nStep 1 is to get the corpora.\nPrinting full word distribution now.")
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, codecs, sys, sqlite3
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from gensim import corpora, models
import random
random.seed(1000)
from sklearn.decomposition import LatentDirichletAllocation
from time import time
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from sklearn.svm import SVC
from sklearn import metrics

global location
global startDate
global endDate
global pattern
global notopics
global stopwords
global regPattern
global splits
global i
global topic_frequency_dicts

date_list = []
earliest_date =datetime(2015,9,1)
latest_date =datetime(2015,9,30)
date_list_1= [date_list.append(datetime(2015,9,day)) for day in range(1,31) ]

assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
early_date_set = set()
regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)
splits=[]


regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)


def returnStories(location):
    f = codecs.open(location,'r',"utf-8")
    for line in f:
        a = json.loads(line)
        yield a
      
    f.close()



def filterWords(d):
    #get texts and filter stopwords
    words = regPattern.sub(' ',d['content'].lower())
    words = word_tokenize(words)
    words = [*filter(lambda x:  not x.lower() in stopwords,words)]
    return words
    
    
def createTopics(words,set_eta,set_alpha):
    n_features = 10000
    n_topics = 300
    n_top_words = 15

    # Use term counts as features for LDA.
    #print("Extracting tf features for LDA...")
    tf_vectorizer = CountVectorizer(max_df=0.65, min_df=1,
                                    max_features=n_features,
                                    stop_words='english')

    tf = tf_vectorizer.fit_transform(words)
    print ("Transformed words into vectors")
    print(datetime.now().strftime('%H:%M:%S'))
    #print("Fitting LDA models")
    lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)

    lda.fit(tf)
    print ("Model fitted")
    print(datetime.now().strftime('%H:%M:%S'))
    pickle.dump(lda, open("model_split_"+str(i)+"_"+str(n_topics)+"topics.pck","wb"))
    print("Model saved")
    print(datetime.now().strftime('%H:%M:%S'))
    doc_topic_distrib = lda.transform(tf)
    print ("Transformed into lda.transform")
    print(datetime.now().strftime('%H:%M:%S'))

    def print_top_words(model, feature_names, n_top_words):
        for topic_idx, topic in enumerate(model.components_):
            #print("Topic #%d:" % topic_idx)
            print(" ".join([feature_names[i]
                            # another numpy fancy indexing trick: `array[startIndex:stopIndex:step]`
                            for i in topic.argsort()[:-n_top_words - 1:-1]]))
            print()
    
    print("\nTopics in LDA model:")
    tf_feature_names = tf_vectorizer.get_feature_names()
    print_top_words(lda, tf_feature_names, n_top_words)
    print ("Printed words")
    print(datetime.now().strftime('%H:%M:%S'))
    
    # #step 1
    # dictionary = corpora.Dictionary(words)
    # dictionary.save('dictionary.dict')

    # #step 2
    # #convert to bag of words
    # corpus = map (dictionary.doc2bow, words)
    # corpora.MmCorpus.serialize('corpus_experiment.mm', corpus)
    # mm_corpus = corpora.MmCorpus('corpus_experiment.mm')
    # print(mm_corpus)
    # tfidf = models.TfidfModel(corpus)
    # corpus_tfidf = tfidf[corpus]
       
    # lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=notopics,eta=set_eta, alpha=set_alpha )
    # corpus_lda = lda[corpus_tfidf]
        

    # #step 3
    # #save topic models
    # #These are models that you use to make topic inferences about documents
    # lda.save('model0_notopics_'+str(notopics)+'_eta_'+str(set_eta)+'_alpha_'+str(set_alpha)+'.lda') 
    # # pickle.dump(corpus_lda, open("corpus_lda_experiment.pck","wb"))                
    # # pickle.dump(tfidf, open("tfidf_experiment.pck","wb"))
   
    # # can add in other types of topic modelling
    # # print ("for eta = ",eta)
    # # print(type(lda))
    # print("Showing topics")
    # # show_topic = lda.show_topic(0, topn=10)
    # # print(show_topic)
    # for topic_no in range(0,10):
        # show_topic = lda.show_topic(topic_no, topn=30)
        # print("Topic no:"+str(topic_no),(show_topic))
    # # print("Get topic term")
    # # get_topic = lda.get_topic_terms(0, topn=len(dictionary))
    # # print(get_topic)


def sortFunction(d):
    
    key ="published"
    if key not in d:
        return False

    dictDate =d[key]
    #remove time portion
    dictDate = dictDate.split("T")[0]
    dictDate = datetime.strptime(dictDate, pattern)

    if dictDate >= startDate and dictDate <= endDate:
        return True
    
def filterDates(d):
    key ="published"
    if key not in d:
        return False

    dictDate =d[key]
    #remove time portion
    dictDate = dictDate.split("T")[0]
    dictDate = datetime.strptime(dictDate, pattern)

    if dictDate >= startDate and dictDate <= endDate:
        return True
  
if __name__ == "__main__":

    pattern = "%Y-%m-%d"

    #startDate = sys.argv[2]
    startDate = "2015-09-07"
    startDate =  datetime.strptime(startDate, pattern)

    #endDate = sys.argv[3]
    endDate = "2015-09-08"
    endDate =  datetime.strptime(endDate, pattern)
    stopwords = set(stopwords.words('english'))
    
    offsets = list(range(11))
    random.shuffle(offsets)
    offsets =offsets[0:9]
    # print(offsets)
    f1st_sep = assumed_earliest_date #fst_sep is the first of september 2015
    
    global startdate
    for r in range(0,9):
        current_line={'Offset': offsets[r], 'Train start date': f1st_sep+timedelta(days=offsets[r]), 'Train end date': f1st_sep+timedelta(days=offsets[r]+8), 'Test start date': f1st_sep+timedelta(days=offsets[r]+9), 'Test end date': f1st_sep+timedelta(days=offsets[r]+17)}
        splits.append(current_line)
    
    location ="sample-1M.jsonl"
    #location =  sys.argv[1]
    if not os.path.isfile(location):
        print ("File %s does not exist" % (location))
        exit()
        
        
   

    
   
    # for notopics in [25,50,100,200]:   
        # i=1
        # print("\n\n\nNumber of topics = ",notopics)
        # print(datetime.now().strftime('%H:%M:%S'))
    i=1
    for dict in splits:
        if i==2:
                break
        startDate = dict['Train start date']
        endDate = dict['Train end date']
        #build topic models
        print ("Starting")
        print(datetime.now().strftime('%H:%M:%S'))
        results = [*filter(filterDates,returnStories(location))]
        print ("Extracted documents- Iteration",(i))
        print(datetime.now().strftime('%H:%M:%S'))
        test_corpus = [*map(filterWords,results)]
        print ("pre-processed and filtered")
        print(datetime.now().strftime('%H:%M:%S'))
        # eta_list = [1/5000, 1/100000, 1/1000000, 0.1,100]
        # for eta_value in eta_list:
            # print("eta =",eta_value)
            # createTopics(test_corpus,eta = eta_value)
            
        #converting list ob=ject to string because throwing error in sklearn tokenizer
        
        test_corpus_string = [str(e) for e in test_corpus]
        print ("Converted to list objects")
        print(datetime.now().strftime('%H:%M:%S'))
        createTopics(test_corpus_string,set_eta = 1/100000, set_alpha= 1/100000)
        # if i==2:
        #        break
        i=i+1
        

    

sys.stdout = orig_stdout
f.close()

