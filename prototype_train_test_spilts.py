import json, codecs, sys
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from datetime import datetime, timedelta
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


assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
early_date_set = set()
regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)
date_list = []
splits=[]
testint = 10
print("test:",testint)

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
    dictionary.save("dictionary"+str(i)+".dict")

    #step 2
    #convert to bag of words
    corpus = map (dictionary.doc2bow, words)
    corpora.MmCorpus.serialize("corpus."+str(i)+"mm", corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
       
    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=notopics)
    corpus_lda = lda[corpus_tfidf]
        

    #step 3
    #save topic models
    #These are models that you use to make topic inferences about documents
    lda.save("model."+str(i)+"lda") 
    pickle.dump(corpus_lda, open("corpus_lda."+str(i)+"pck","wb"))                
    pickle.dump(tfidf, open("tfidf."+str(i)+"pck","wb"))
    print ("done")
    
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
    location ="sample-1M.jsonl"
    #location =  sys.argv[1]
    if not os.path.isfile(location):
        print ("File %s does not exist" % (location))
        exit()
    
    
    offsets = list(range(11))
    random.shuffle(offsets)
    offsets =offsets[0:9]
    print(offsets)
    f1st_sep = assumed_earliest_date #fst_sep is the first of september 2015
    
    global startdate
    for r in range(0,9):
        current_line={'Offset': offsets[r], 'Train start date': f1st_sep+timedelta(days=offsets[r]), 'Train end date': f1st_sep+timedelta(days=offsets[r]+8), 'Test start date': f1st_sep+timedelta(days=offsets[r]+9), 'Test end date': f1st_sep+timedelta(days=offsets[r]+17)}
        splits.append(current_line)
    
    print(splits)
 
    #notopics = sys.argv[4]
    notopics = 300

    stopwords = set(stopwords.words('english'))
    
    i=0
    for dict in splits:
        startDate = dict['Train start date']
        endDate = dict['Train end date']
        #build topic models
        results = filter(filterDates,returnStories(location))
        print ("sorted- Iteration",(i+1))
        words = map(filterWords,results)
        print ("pre-processed")
        createTopics(words)
        i=i+1
