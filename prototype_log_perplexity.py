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
print("Printing log_perplexity for models with 800 AND 900 TOPICS.")

import json, codecs, sqlite3
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
global splits
global i
global topic_frequency_dicts

# Insert the saved model here to print out the 
# model0_words = pickle.load(open("model0_notopics_300_eta_1e-06.lda","rb"))
# print(model0_words) 
notopics_list = range(800,1000,100)
stopwords = set(stopwords.words('english'))

def calculatePerplexity(words):
    dictionary = corpora.Dictionary(words)
    dictionary.save("dictionary_"+str(i)+"_"+str(notopics)+"topics.dict")

    global global_dict
    global_dict = dictionary

    #step 2
    #convert to bag of words
    corpus = map (dictionary.doc2bow, words)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    perplexity = lda.log_perplexity(corpus_tfidf, total_docs=None)
    return perplexity
   
    
for notopics in notopics_list:
    #start_time = time.time()
    i=1
    print("Loading topic model with  number of topics = ",notopics)
    lda = models.LdaModel.load("/home/sai/project/scripts/model_"+str(i)+"_"+str(notopics)+"topics.lda")
    print("Topic model loaded",datetime.now())
    # model0_topic_words = {}
    # print("Showing topic 0 ")
    # lda.print_topics(num_topics=20, num_words=10)
    # top20_words = lda.show_topic(0, topn=20)
    # print(top20_words)
    # for topic in range(10):
        # print(topic)
        # lda.print_topics(num_topics=20, num_words=10)
        # top20_words = lda.show_topic(topic, topn=20)
        # print(top20_words)
    test_corpus = pickle.load(open("/home/sai/project/scripts/test_sample.pck","rb"))
    perplexity = calculatePerplexity(test_corpus)
    print("Perplexity = ",perplexity)
    # if i==2:
    #        break
    i=i+1
    print("------")
    

# lda.get_topic_terms(0, topn=10)

# for i in range(0,300): 
    # model0_topic_words["topic_"+str(i)]=lda.print_topic(i,topn=10)

# pickle.dump(model0_topic_words,open("model0_topic_words_top10.pck","wb"))