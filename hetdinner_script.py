# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 19:17:49 2020

@author: gcvic
"""

from tika import parser
#from pylatexenc.latexencode import unicode_to_latex
import pandas as pd
import requests
import os
import googletrans
#import latex_templates
from emoji import  demojize
from matplotlib import pyplot as plt
import nltk
# from googletrans import Translator
from google_trans_new import google_translator
from collections import defaultdict
from mtranslate import translate
import tqdm
import random
import time
import pickle
import copy
import re

debug = 0
to_txt = True
load_translation = False
filename = 'Het_diner'
title = 'Het Diner'
source_lang = 'nl'
target_lang = 'en'
tokenizer_lang = 'english'


random.seed(7)

print("Reading text...")
folder = r'C:\Users\gcvic\Documents\bilingual-document-generator'
raw = parser.from_file(os.path.join(folder, r"hetdinner_pdf_dutch.pdf"))
safe_text = raw['content']#.encode('utf-8', errors='ignore')
print('Cleaning...')
raw = str(safe_text)#.replace("\n", "").replace("\\", "")
print(len(raw))
# raw = raw.replace('www.writingshome.com', '')
#.replace('Fëdor Michailovic Dostoevskij  - I fratelli Karamazov', '')
import re
print(len(raw))
regex = re.compile('\n+')
raw = regex.sub('\n',raw).replace('\n', ' ')
print(len(raw))
print("%d characters read" % len(raw))

# AD-hoc transformation
# raw = raw.replace('[', '').replace(']', '')



tokenizer_path = 'tokenizers/punkt/%s.pickle' % tokenizer_lang
print('Tokenizing with %s...' % tokenizer_path)
tokenizer = nltk.data.load(tokenizer_path)
prep = raw
prep = prep.replace('.', '. ')
prep = prep.replace('. . . ', '... ')
prep = prep.replace('?', '? ')

tokens = tokenizer.tokenize(prep)
if debug:
    print("Sampling tokens...")
    time.sleep(.5)
    size = min(500, len(tokens))
    tokens = random.sample(tokens, size)
def parse_token(t):
    t = re.sub(r'\.{3,}', "...", t)
    
    return t
print("Parsing %d tokens..." % len(tokens))
tokens = [parse_token(t) for t in tqdm.tqdm(tokens)]

print('PLotting before...')
plt.figure()
pd.Series([len(t) for t in tokens]).plot.hist(bins = 200,
                                              title = 'Token length HIST before')
plt.show()
plt.figure()
pd.Series([len(t) for t in tokens]).plot.hist(bins = 200,
                                              title = 'Token length CDF before', cumulative = True, density = True)
plt.show()

i=0


def clean(tokens, sep):
    ts = []
    MAX_SENTENCE_LEN = 150
    for t in tokens:
        if len(t) <= MAX_SENTENCE_LEN or sep not in t:
            ts.append(t)
        else:
            print('------------------------')
            print('BIG', t)
            
            remainder = t.split(sep)[::-1]
               
            add = []
            while remainder:
                add.append(remainder.pop())
                if len(sep.join(add)) >= .7*MAX_SENTENCE_LEN:
                    nt =  sep.join(add)
                    if len(remainder) > 0:
                        nt += sep
                    print('-',nt)
                    ts.append(nt)
                    add = []
            if len(add) > 0:
                nt = sep.join(add)
                print('*',nt)
                ts.append(nt)
            # ts[-1] = ts[-1] + ','
            
                
    tokens = ts.copy()
    return tokens
for sep in [',', ':', '?', '!']:
    print('CLEANING', sep)
    tokens = clean(tokens, sep)


tokens = [t for t in tokens if t != '']
print('PLotting after...')
plt.figure()
pd.Series([len(t) for t in tokens]).plot.hist(bins = 200,
                                              title = 'Token length HIST after')
plt.show()
plt.figure()
pd.Series([len(t) for t in tokens]).plot.hist(bins = 200,
                                              title = 'Token length CDF after', cumulative = True, density = True)
plt.show()     
        


chunks = []
max_chunksize = 2000
chunk = []
for token in tqdm.tqdm(tokens, desc = 'Creating chunks'):
    if (len(sep) * len(chunk)+sum([len(t) for t in chunk + [token]])) < max_chunksize:
        chunk.append(token)
    else:
        if len(chunk) > 0:
            chunks.append(chunk)
        chunk = []
chunks.append(chunk)

print('Plotting')

plt.figure()
pd.Series([len(''.join(c)) for c in chunks]).plot.hist(bins = 200,
                                              title = 'Chunk length')   
plt.show()
import random
filename = 'translations_%s.pickle' % title.replace(' ', '_')
translator = google_translator()
srcs = []
targets = []


translations = defaultdict(str)
print("Translating %d..." % len(chunks))
for i, ts in tqdm.tqdm(enumerate(chunks),
                      desc = 'Translating',
                      total = len(chunks)):
   
    if i < 979:
        pass
    while 1:
        sep = '\n'+str(random.randint(10000, 99999)) + '\n'
        t = sep.join(ts)
       
        demojized_token = demojize(t)
        # translation = translate(demojized_token, target_lang)
        try:
            translation = translator.translate(demojized_token, 
                                               lang_src=source_lang, lang_tgt=target_lang)
        except Exception as e:
            print('ERROR:', str(e))
            secs = 10 + random.random() * 40 
            time.sleep(secs)
            continue
        assert isinstance(translation, str), translation
        assert len(translation) > 0, translation
        
        src = ts
        target = translation.split(sep.strip())
        if len(src) != len(target):
            print('ERROR')
            secs = 5 + random.random() * 40
            time.sleep(secs)
            continue
        
        src = [s.strip() for s in src]
        target = [s.strip() for s in target]
        for k, (s, t) in enumerate(zip(src, target), 1):
            print('----------------------------------------------------')
            print(f'chunk {i}/{len(chunks)}, token {k}/{len(target)}')
            print('-',s)
            print('+',t)
        
        srcs.append(src)
        targets.append(target)
        # translations[i] = translation#.text
        secs = 10 + random.random() * 10
        print('*************************')
        time.sleep(secs)
        break




def lreplace(pattern, sub, string):
    return re.sub('^%s' % pattern, sub, string)

def rreplace(pattern, sub, string):
    return re.sub('%s$' % pattern, sub, string)
print('Replacing artifacts...')
targets = [t.replace(' #', '').replace('# ', '').strip()\
           for t in tqdm.tqdm(targets)]

flatten = lambda t: [item for sublist in t for item in sublist]
srcs = flatten(srcs)
targets = flatten(targets)

print('Generating txt...')
result = []
for src, target in zip(srcs, targets):
    #result.append('$ %s' % src)
    line = src + '>>>>' + target
    result.append(line)
    # result.append('_ %s' % target)

result = '\n\n'.join(result)

name = '%s.txt' % title.replace(' ', '_')
filepath = os.path.join(r'C:\Users\gcvic\Documents\bilingual-document-generator\%s' % name)
with open(filepath, 'w', encoding='utf8') as fp:
    fp.write(result)
print("Goed gedaan!", filepath)
    
