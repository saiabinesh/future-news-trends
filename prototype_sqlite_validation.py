import json, codecs, sys, sqlite3
import os.path, string
import re, pickle, datetime

conn = sqlite3.connect('db\models.db')
c = conn.cursor()
date = ("2015-09-02 00:00:00",)
c.execute('SELECT COUNT(*) FROM Test WHERE Date =?',date )
print(c.fetchone()[0])
conn.commit()
conn.close()