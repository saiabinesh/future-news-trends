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
print("Getting the time between inferences between windows and linux machibne for 500 docs")

import json, codecs, sqlite3
import os.path, string
import re, pickle
import gensim, nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from gensim import corpora, models
import random
random.seed(1000)
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
global splits
global i
global topic_frequency_dicts

# Insert the saved model here to print out the 
# model0_words = pickle.load(open("model0_notopics_300_eta_1e-06.lda","rb"))
# print(model0_words) 

def returnStories_json(location):
    f = codecs.open(location,'r',"utf-8")
    for line in f:
        a = json.loads(line)
        yield a
    f.close()

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
    words = regPattern.sub(' ',d['content'].lower())
    # words = d[1]
    # return words.split()
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
      
def inferTopics_new(words):
    dictionary = corpora.Dictionary(words)
    global global_dict
    global_dict = dictionary
    #step 2
    #convert to bag of words
    corpus = map (dictionary.doc2bow, words)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    print("Loading topic model in split ",i)
    lda = models.LdaModel.load("/home/sai/project/scripts/model_"+str(i)+"_"+str(notopics)+"topics.lda")
    # The following line of code gets topic probability distribution for given 
    corpus_lda = lda[corpus_tfidf]
    
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

def inferTopics(test_corpus,split_offset):
    global i
    topic_frequency_dicts=[]
    
    #Creating a list of dictionaries that will act like rows to be appended into the database containing the topic frequencies
    f1st_sep = datetime(2015, 9, 1, 0, 0) 
    for index in range(0,700):
        for r in range(0,17):
            # print(f1st_sep+timedelta(days=split_offset+r))
            temp_dict = {"Topic_no" : index, "Date":f1st_sep+timedelta(days=split_offset+r), "No._of_days":9, "Unigrams": 1,"Iteration":i, "Frequency":0}
            topic_frequency_dicts.append(temp_dict)
    
    #step 1 - Load the dictionary and lda model for the split
    #Store the words in a dictonary format
    test_dictionary = corpora.Dictionary.load("/home/sai/project/scripts/dictionary_"+str(i)+"_"+str(notopics)+"topics.dict")
    #loading the previously saved topic model.These are models that used to make topic inferences about documents
    lda = models.LdaMulticore.load("/home/sai/project/scripts/model_"+str(i)+"_"+str(notopics)+"topics.lda")
    print("Topic model for split "+str(i)+" loaded")
    print(datetime.now().strftime('%H:%M:%S'))
 
    #step 3
    #convert to bag of words
    document_number  = 0
    for json_doc in test_corpus:
        if (document_number == 500):
            break
        tokenized_json_doc = filterWords(json_doc)
        bag_of_words_json_doc = test_dictionary.doc2bow(tokenized_json_doc)
        # print(bag_of_words_json_doc)
        inferred_lda_vector= lda[bag_of_words_json_doc]
        # print(len(inferred_lda_vector))
        # print(inferred_lda_vector)
        # print("type(lda)",type(lda))
        # print("type(inferred_lda_vector)",type(inferred_lda_vector))
        
        for topic_no,probability in inferred_lda_vector:
            for dict in topic_frequency_dicts:
                if (dict["Topic_no"]==topic_no):
                    if(dict["Date"]==datetime.strptime(json_doc["published"].split("T") [0],"%Y-%m-%d")):
                        if(dict["Iteration"]==i):                      
                            dict["Frequency"]=dict["Frequency"]+1 #If the topic appears with any probablity at all, then it is added in the frequency count of that timeseries for that date
                            break
        
        document_number = document_number + 1
    # pickle.dump(topic_frequency_dicts, open("topic_frequency_dicts_25docs_"+str(i)+".pck","wb"))
    list_of_lists = []
    for dict in topic_frequency_dicts:
        dict['Date'] = str(dict['Date'])
        # print(dict["Date"])
        # exit()
        temp_tuple = tuple(dict.values())
        list_of_lists.append(temp_tuple)
        
    c.executemany('INSERT INTO topic_frequencies_test VALUES(?,?,?,?,?,?)', list_of_lists)
    conn.commit()

# The function to get the splits which is not necessary to be used as we can load it from the saved file
def splits():
    assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
    random.seed(1000)
    offsets = list(range(11))
    random.shuffle(offsets)
    offsets =offsets[0:9]
    # print(offsets)
    f1st_sep = assumed_earliest_date #fst_sep is the first of september 2015
    splits=[]
    global startdate

    #Getting the splits from the saved file
    for r in range(0,9):
        current_line={'Offset': offsets[r], 'Train start date': f1st_sep+timedelta(days=offsets[r]), 'Train end date': f1st_sep+timedelta(days=offsets[r]+8), 'Test start date': f1st_sep+timedelta(days=offsets[r]+9), 'Test end date': f1st_sep+timedelta(days=offsets[r]+17)}
        splits.append(current_line)

    print(splits)
    pickle.dump(splits,open("splits.pck","wb"))

start_time_filtering = datetime.now()

   
assumed_earliest_date = datetime(2015, 9, 1, 0, 0)
early_date_set = set()
regPattern = "[^a-z\s-]"
regPattern = re.compile(regPattern)
conn = sqlite3.connect('/home/sai/project/data/topic_frequencies_500_docs.db')
c = conn.cursor()
# Creating a new database table Test_25_6
c.execute("CREATE TABLE topic_frequencies_test ( `Topic_No.` INTEGER NOT NULL, `Date` TEXT NOT NULL, `No._of_days` INTEGER NOT NULL, `Unigrams` INTEGER NOT NULL, `Iteration` INTEGER NOT NULL, `Frequency` INTEGER NOT NULL );")
print("Created new database table topic_frequencies_test")

i=1
pattern = "%Y-%m-%d"
#Getting the splits from the saved file
splits = pickle.load(open("splits.pck","rb"))
stopwords = set(stopwords.words('english'))
notopics = 700
location ="/home/sai/project/data/signalmedia-1m.jsonl"

i=1
print("Topic Inferences phase")
start_time_topic_inference = datetime.now().strftime('%H:%M:%S')
print(start_time_topic_inference)
for dict in splits:
    if i==2:
        break
    startDate = dict['Train start date']
    endDate = dict['Test end date']
    #Get topic inferences
    start_time_filtering = datetime.now()
    results = filter(filterDates,returnStories_json(location))
    end_time_filtering = datetime.now()
    print("Time for filtering dates in split = ", (end_time_filtering - start_time_filtering).total_seconds())
    inferTopics(results,dict['Offset'])
    print(datetime.now().strftime('%H:%M:%S'))
    # exit()
    # if i==2:
    #     break
    i=i+1

end_time_filtering = datetime.now() 
print("Time for inferring 500 docs in split 1  = ", (end_time_filtering - start_time_filtering).total_seconds())
conn.close()
exit()


