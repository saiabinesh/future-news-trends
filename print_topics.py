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
print("Looking at the words in model0")

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

model0_words = pickle.load(open("model0_topic_words_top10.pck","rb"))
print(model0_words) 

# print("Loading topic model",datetime.now())
# lda = models.LdaModel.load("model0.lda")  
# print("Topic model loaded",datetime.now())
# model0_topic_words = {}
# print("Showing topic")
# lda.show_topic(0, topn=10)
# print("Get topic term")
# lda.get_topic_terms(0, topn=10)

# for i in range(0,300): 
    # model0_topic_words["topic_"+str(i)]=lda.print_topic(i,topn=10)

# pickle.dump(model0_topic_words,open("model0_topic_words_top10.pck","wb"))