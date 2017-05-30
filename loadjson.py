#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    words = filter(lambda x:  not x.lower() in stopwords,words)
    return words
    
    
def createTopics(words):
    #step 1
    dictionary = corpora.Dictionary(words)
    dictionary.save('dictionary.dict')

    #step 2
    #convert to bag of words
    corpus = map (dictionary.doc2bow, words)
    corpora.MmCorpus.serialize('corpus.mm', corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
       
    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=notopics)
    corpus_lda = lda[corpus_tfidf]
        

    #step 3
    #save topic models
    #These are models that you use to make topic inferences about documents
    lda.save('model.lda') 
    pickle.dump(corpus_lda, open("corpus_lda.pck","wb"))                
    pickle.dump(tfidf, open("tfidf.pck","wb"))
   

    #can add in other types of topic modelling

    
    print ("done")


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
    
   
  
if __name__ == "__main__":

    pattern = "%Y-%m-%d"

    #startDate = sys.argv[2]
    startDate = "2015-09-07"
    startDate =  datetime.strptime(startDate, pattern)

    #endDate = sys.argv[3]
    endDate = "2015-09-08"
    endDate =  datetime.strptime(endDate, pattern)
    
    #notopics = sys.argv[4]
    notopics = 300
    
    location ="sample-1M.jsonl"
    #location =  sys.argv[1]
    if not os.path.isfile(location):
        print ("File %s does not exist" % (location))
        exit()

    stopwords = set(stopwords.words('english'))
    
    results = filter(sortFunction,returnStories(location))
    print ("sorted")

    #build topic models
    words = map(filterWords,results)
    print ("pre-processed")
    createTopics(words)
    print ("done")


