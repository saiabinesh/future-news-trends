#Below class displays output in console as well as logging it in a logfile.log file
import sys

orig_stdout = sys.stdout
f = open('logfile.log', 'a')
sys.stdout = f

from datetime import datetime, timedelta
print("\nExperiment time: ",datetime.now())
print("Objective: Getting topic models with low values for both alpha and eta. Looking at the top 20 words in the first 10 topics. For different values of eta")
# increase the eta parameter and check the results.\nStep 1 is to get the corpora.\nPrinting full word distribution now.")
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, codecs
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
    words = [*filter(lambda x:  not x.lower() in stopwords,words)]
    return words
    
    
def createTopics(words,eta):
    #step 1
    dictionary = corpora.Dictionary(words)
    dictionary.save('dictionary.dict')

    #step 2
    #convert to bag of words
    corpus = map (dictionary.doc2bow, words)
    corpora.MmCorpus.serialize('corpus_experiment.mm', corpus)
    mm_corpus = corpora.MmCorpus('corpus_experiment.mm')
    print(mm_corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
       
    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=notopics, eta=eta)
    corpus_lda = lda[corpus_tfidf]
        

    #step 3
    #save topic models
    #These are models that you use to make topic inferences about documents
    # lda.save('model_experiment.lda') 
    # pickle.dump(corpus_lda, open("corpus_lda_experiment.pck","wb"))                
    # pickle.dump(tfidf, open("tfidf_experiment.pck","wb"))
   

    #can add in other types of topic modelling
    print ("for eta = ",eta)
    # print(type(lda))
    print("Showing topic")
    # show_topic = lda.show_topic(0, topn=10)
    # print(show_topic)
    for topic_no in range(0,50):
        show_topic = lda.show_topic(topic_no, topn=10)
        print("Topic no:"+str(topic_no),(show_topic))
    # print("Get topic term")
    # get_topic = lda.get_topic_terms(0, topn=len(dictionary))
    # print(get_topic)


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
    # documents_7thand8thSep = [*filter(sortFunction,returnStories(location))]
    # pickle.dump(documents_7thand8thSep,open("documents_7thand8thSep.pck","wb"))
    documents_7thand8thSep = pickle.load(open("documents_7thand8thSep.pck","rb"))
    results = documents_7thand8thSep[0:50]
    # print(type(results))
    # print(len(results))
    # print(results[0])
    print ("sorted")
    #build topic models
    words = [*map(filterWords,results)]
    print ("pre-processed")
    eta_list = [0.01,0.001,0.1,0,1,2,5,10,100]
    for eta in eta_list:
            createTopics(words,eta = eta)
    print ("done")

sys.stdout = orig_stdout
f.close()

