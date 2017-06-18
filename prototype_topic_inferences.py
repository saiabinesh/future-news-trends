#Below class displays output in console as well as logging it in a logfile.log file
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
print("Step 1 is initializing a topic_frequency_dicts with a dictionary each for each of the 300 topics. these dictionaries will later be dumped into sqllite\n Has been successful\n Step 2 get topic inference for 1 document in the first split of 1 day and update the topic frequencies in the topic_frequency_dicts")

import json, codecs, sys, sqlite3
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
topic_frequency_dicts=[]
for index in range(0,300):
    temp_dict = {"Topic_no" : index, "Date":"", "No._of_days":9, "Unigrams": 1,"Iteration":0, "Frequency":0}
    topic_frequency_dicts.append(temp_dict)
#print(topic_frequency_dicts)


assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
early_date_set = set()
regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)
splits=[]
conn = sqlite3.connect('db\models.db')
c = conn.cursor()



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
    corpora.MmCorpus.serialize("corpus"+str(i)+".mm", corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
       
    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=notopics)
    corpus_lda = lda[corpus_tfidf]
    
    #step 3
    #save topic models
    #These are models that you use to make topic inferences about documents
    lda.save("model"+str(i)+".lda") 
    pickle.dump(corpus_lda, open("corpus_lda"+str(i)+".pck","wb"))                
    pickle.dump(tfidf, open("tfidf"+str(i)+".pck","wb"))
    print ("Topic modelling for split"+str(i+1)+": done")
    print(datetime.now().strftime('%H:%M:%S'))
    
def inferTopics(test_corpus):
    global i
    #step 1 - Load the dictionary and lda model for the split
    #Store the words in a dictonary format
    test_dictionary = corpora.Dictionary.load("dictionary"+str(i)+".dict")
    
    #loading the previously saved topic model.These are models that used to make topic inferences about documents
    lda = models.LdaModel.load("model"+str(i)+".lda")
    print("Topic model for split "+str(i)+" loaded")
    print(datetime.now().strftime('%H:%M:%S'))
    
    #probably need loop through words which is a representation of the whole corpus
    #step 3
    #convert to bag of words
    for json_doc in test_corpus:
        tokenized_json_doc = filterWords(json_doc)
        bag_of_words_json_doc = test_dictionary.doc2bow(tokenized_json_doc)
        #print(bag_of_words_json_doc)
        inferred_lda_vector= lda[bag_of_words_json_doc]
        print(len(inferred_lda_vector))
        print(inferred_lda_vector)
        # print("type(lda)",type(lda))
        # print("type(inferred_lda_vector)",type(inferred_lda_vector))
        
        for topic_no,probability in inferred_lda_vector:
            for dict in topic_frequency_dicts:
                if (dict["Topic_no"]==topic_no):
                    dict["Date"]=datetime.strptime(json_doc["published"].split("T") [0],"%Y-%m-%d")
                    dict["Frequency"]=dict["Frequency"]+1 #If the topic appears with any probablity at all, then it is added in the frequency count of that timeseries for that date
                    dict["Iteration"]=i
                    break
                topic_frequency_dicts.append(dict)
                
        print(topic_frequency_dicts)
        exit()
            
        # pattern = "%Y-%m-%d"
        # key ="published"
        # if key not in d:
        #     return False
        # dictDate =json_doc[key]
        # #remove time portion
        # dictDate = dictDate.split("T")[0]
        # dictDate = datetime.strptime(dictDate, pattern)
        # Unigrams = 1
        # No._of_days = 9
        # row = [(Unigrams, topic_no, dictDate, i, No._of_days, 
        # # Insert a row of data
        # c.execute('INSERT INTO Test VALUES (?,?,?,?,?)', purchases)
        # 
        # # Save (commit) the changes
        # conn.commit()
        # 
        # # We can also close the connection if we are done with it.
        # exit()
        # print ("")
        # a= max([l[1] for l in inferred_lda_vector])
        # for i in inferred_lda_vector:
        #     if i[1]==a:
        #         print (i)
        #end_time_single_document = datetime.now().strftime('%H:%M:%S')
        #print(end_time_single_document)
        #print("Time for a single document topic inference = ", (end_time_single_document - start_time_topic_inference).total_seconds())
    
    #print(datetime.now().strftime('%H:%M:%S'))


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
    
    splits = pickle.load(open("splits.pck","rb"))
    print(splits[8]['Test start date'])
    notopics = 300
    stopwords = set(stopwords.words('english'))
    
    # i=1
    # print("Topic modelling phase")
    # print(datetime.now().strftime('%H:%M:%S'))
    # for dict in splits:
    #     startDate = dict['Train start date']
    #     endDate = dict['Train end date']
    #     #build topic models
    #     results = [*filter(filterDates,returnStories(location))]
    #     print ("Extracted documents- Iteration",(i+1))
    #     test_corpus = [*map(filterWords,results)]
    #     print ("pre-processed")
    #     print(datetime.now().strftime('%H:%M:%S'))
    #     createTopics(test_corpus)
    #     # if i==2:
    #     #        break
    #     i=i+1

    i=1
    print("Topic Inferences phase")
    start_time_topic_inference = datetime.now().strftime('%H:%M:%S')
    print(start_time_topic_inference)
    for dict in splits:
        startDate = dict['Train start date']
        endDate=startDate
        #endDate = dict['Test end date']
        print(startDate)
        #Get topic inferences
        start_time_filtering = datetime.now()
        results = [*filter(filterDates,returnStories(location))]
        end_time_filtering = datetime.now()
        print("Time for filtering dates in split = ", (end_time_filtering - start_time_filtering).total_seconds())
        inferTopics(results)
        #print(datetime.now().strftime('%H:%M:%S'))
        if i==2:
            break
        i=i+1
    
    conn.close() #closing the database connection    
