import sys
import numpy as np
import statsmodels.api as statsmodels
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
print("Trying to print topics from a model.  Trying top n=10 explicity")

import pickle

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
numpy_array_topic_frequencies = np.zeros(shape=(9,300))
numpy_array_topic_frequencies = pickle.load(open("numpy_array_topic_frequencies_1.pck","rb"))

a = statsmodels.tsa.stattools.grangercausalitytests(numpy_array_topic_frequencies[:,[1,0]], 1, addconst=True, verbose=True)

print((a[1][0]))

causality_pairs = pickle.load(open("causality_pairs_p_values.pck","rb"))
print(causality_pairs)

