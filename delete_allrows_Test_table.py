import json, codecs, sys, sqlite3
import os.path, string
import re, pickle, datetime

conn = sqlite3.connect('db\models.db')
c = conn.cursor()
c.execute('DELETE FROM Test_25_6')
conn.commit()
conn.close()