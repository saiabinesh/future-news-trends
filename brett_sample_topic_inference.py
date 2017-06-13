
import json, codecs, sys
import time
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from datetime import datetime
from gensim import corpora, models
from nltk import ngrams



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

regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)

gc = 0
globalCount = 0


def returnStories(location):
    f= open(location)
    for line in f:
        a = json.loads(line)
        yield a
      
    f.close()




def returnNgrams(sentence,n=3):
    words = [" ".join(w).strip() for w in ngrams(word_tokenize(sentence),n) if not set(w).intersection(stopwords)]
    return words


def filterWords(d):
    #get texts and filter stopwords
    words = regPattern.sub(' ',d['content'].lower())
    words = word_tokenize(words)
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

   
       
    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=notopics)
    corpus_lda = lda[corpus_tfidf]

    global global_lda
    global_lda = lda   

    #step 3
    #save topic models
    #These are models that you use to make topic inferences about documents
    lda.save('model.lda') 
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
    
    
def inferTopic(docs):
    global global_lda
    global global_dict

    for doc in docs:
        bw = global_dict.doc2bow(doc["content"].split())
        lda_vector = global_lda[bw]
        print(lda_vector)
        print ""
        a= max([l[1] for l in lda_vector])
        for i in lda_vector:
            if i[1]==a:
                print i
                exit()
        exit()
    



if __name__ == "__main__":

    pattern = "%Y-%m-%d"

    #startDate = sys.argv[2]
    startDate = "2015-09-01"
    startDate =  datetime.strptime(startDate, pattern)

    #endDate = sys.argv[3]
    endDate = "2015-09-30"
    endDate =  datetime.strptime(endDate, pattern)
    
    #notopics = sys.argv[4]
    notopics = 300
    
    location ="/home/sai/project/data/signalmedia-1m.jsonl"
    #location =  sys.argv[1]
    if not os.path.isfile(location):
        print ("File %s does not exist") % (location)
        exit()

    stopwords = set(stopwords.words('english'))

    for gc in range(100,100000, 500):
        start_time = time.time()
        results = filter(sortFunction,returnStories(location))
        print ("sorted")

        #build topic models
        words = map(filterWords,results)
        print ("pre-processed")
   
        createTopics(words)

        #infer topic one story
        s= returnStories(location)
        inferTopic(s)
        
        end_time = time.time()
        print("--- %s seconds --- %d\n" % (end_time - start_time, gc))
        globalCount = 0
    print ("done")

