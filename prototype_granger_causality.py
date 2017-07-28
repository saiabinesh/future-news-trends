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
print("Granger causality works between two columns only. Now checking between column 1 and 2, by making the second column lag by 1 value of the 1st column.")

import json, codecs, sys, sqlite3
import os.path, string
import re, pickle, datetime
import statsmodels.api as statsmodels
import numpy as np

# i=1
# topic_frequency_dicts = pickle.load(open("topic_frequency_dicts_21Jun_25docs_"+str(i)+".pck","rb"))
# list_of_lists = []
# print(topic_frequency_dicts[0])
# exit()

#INitializing a numpy array of size 9 (days) by 300 (topics)
numpy_array_topic_frequencies = np.zeros(shape=(9,300))

# For loop to convert the topic frequency lists into numpy array of inferences with each column having the frequencies of each topic, every row corresponding to the next consecutive day(date) in the current iteration.
# for topic in range(0,300):
    # temp_list_of_topic_dicts = [x for x in topic_frequency_dicts if x["Topic_no"]== topic]
    # for date in range(0,9):
        # numpy_array_topic_frequencies[date,topic] = temp_list_of_topic_dicts[date]["Frequency"]
    
# print([x for x in topic_frequency_dicts if x["Topic_no"]== 2])
# print(numpy_array_topic_frequencies[:,2])

#pickle.dump(numpy_array_topic_frequencies, open("numpy_array_topic_frequencies_1.pck","wb"))
numpy_array_topic_frequencies = pickle.load(open("numpy_array_topic_frequencies_1.pck","rb"))
# print(numpy_array_topic_frequencies[:,])
numpy_array_topic_frequencies_test = numpy_array_topic_frequencies


causality_pairs = {}
for topic_1 in range(0,300):
    for topic_2 in range(0,300):
        if topic_1 != topic_2:
            lr_test_result = statsmodels.tsa.stattools.grangercausalitytests(numpy_array_topic_frequencies[:,[topic_2,topic_1]], 1, addconst=True, verbose=False)[1][0]['lrtest']
            causality_pairs['topic_'+str(topic_1)+'causing topic_'+str(topic_2)]= lr_test_result[1]
            

pickle.dump(causality_pairs, open("causality_pairs_p_values.pck","wb"))

# for i in range(0,9):
    # if i==0:
        # numpy_array_topic_frequencies_test[0,1]=0
    # else:
        # numpy_array_topic_frequencies_test[i,1]=numpy_array_topic_frequencies[i-1,0]
        


# # print(numpy_array_topic_frequencies_test[:,0])
# # print(numpy_array_topic_frequencies_test[:,1])

# a = statsmodels.tsa.stattools.grangercausalitytests(numpy_array_topic_frequencies_test[:,[1,0]], 1, addconst=True, verbose=True)

# # print(type(a)) dict
# # print(type(a[1])) tuple
# # print(type(a[1][0])) dict

# print(a[1][0]['lrtest'])

# # print(a.values())
# # print(a.keys())
# #print(a['lrtest'])
# # print(a['1'])
# # print(a['1']['lrtest'])

# # for i in a.items():
    # # print(i)
    # # print ("")
