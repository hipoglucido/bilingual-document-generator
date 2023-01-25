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
filename = 'I_fratelli_Karamazov'
title = 'I fratelli Karamazov'
author = 'Fyodor'
source_lang = 'it'
target_lang = 'es'
tokenizer_lang = 'italian'


random.seed(7)

print("Reading text...")
folder = r'C:\Users\gcvic\Documents\bilingual-document-generator'
raw = parser.from_file(os.path.join(folder, r"brothers_dost.pdf"))
safe_text = raw['content']#.encode('utf-8', errors='ignore')
print('Cleaning...')
raw = str(safe_text).replace("\n", "").replace("\\", "")
print(len(raw))
raw = raw.replace('www.writingshome.com', '')
#.replace('Fëdor Michailovic Dostoevskij  - I fratelli Karamazov', '')
import re
print(len(raw))
regex = re.compile('Fëdor Michailovic Dostoevskij  - I fratelli Karamazov \d+')
raw = regex.sub('',raw)
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

if load_translation:
    with open(filename, 'rb') as handle:
        translations = pickle.load(handle)
    print("Read %s" % filename)
else:
    translations = defaultdict(str)
    print("Translating %d..." % len(chunks))
    for i, ts in tqdm.tqdm(enumerate(chunks),
                          desc = 'Translating',
                          total = len(chunks)):
       
        if i < 979:
            continue
        while 1:
            sep = '\n'+str(random.randint(10000, 99999)) + '\n'
            t = sep.join(ts)
           
            demojized_token = demojize(t)
            # translation = translate(demojized_token, target_lang)
            try:
                translation = translator.translate(demojized_token, 
                                                   lang_src='it', lang_tgt=target_lang)
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

    with open(filename, 'wb') as handle:
        pickle.dump(translations, handle)
    print("Saved %s" % filename)




# srcs = []
# targets = []
# sep_t = sep.strip() #regexPattern = '|'.join(['-_._-'])
# corrections = [
#     ('tazo al Hyperomonaci "ya se conoce, muy reverendo. Por ', 
#      f'tazo al Hyperomonaci "ya se conoce, muy reverendo. {sep_t} Por '),
#      ('¿Es porque ese "encuesto"', f'¿Es porque ese "encuesto"{sep_t}{sep_t}{sep_t}'),
#      ('sde tu Deringe. Tal vez, quizás, re', f'sde tu Deringe.{sep_t} Tal vez, quizás, re'),
#      ('acordado, señor. Tal vez, en este momen', f'acordado, señor.{sep_t} Tal vez, en este momen'),
#      ('Él había mencionado repetidamente in', f'{sep_t}{sep_t}{sep_t}{sep_t}{sep_t}{sep_t}{sep_t}Él había mencionado repetidamente in'),
#      ('Parecía palabras extrañas', f'{sep_t}Parecía palabras extrañas'),
#      (' de esta historia Está en su mis', f'{sep_t} de esta historia Está en su mis'),
#      ('369 111586', '369111586'),
#      ('e mis pruebas. Por lo', f'e mis pruebas. {sep_t}Por lo'),
#      ('nto. Lamentaban', f'nto. {sep_t}Lamentaban'),
#      ('Pero toda la ciudad se lev', f'{sep_t}{sep_t}{sep_t}Pero toda la ciudad se lev'),
#      ('llí donde está. Casi todos,', f'llí donde está. {sep_t}{sep_t}Casi todos,'),
#      ("o hice. '¡Hubiera regresad", f"o hice. {sep_t}'¡Hubiera regresad"),
#      ('caso. , Que el o', f'caso.{sep_t} , Que el o'),
#      ('niño! Con un tono v', f'niño! {sep_t}Con un tono v'),
#      (' cubiertos., ¿verda', f' cubiertos., {sep_t}{sep_t}¿verda'),
#      ('369111 586', '369111586')
# ]
# for i in tqdm.tqdm(range(len(chunks)), desc = 'Creating columns...'):
#     src = chunks[i].split(sep)
#     target = translations[i]
#     for old, new in corrections:
#         target = target.replace(old, new)
#     target = target.split(sep_t)
#     if i == -1:
#         j = 0
#         while 1:
#             print(f'\nj={j}--------------------------')
#             print(f'>>{src[j]}')
#             print(f'>>{target[j]}')
#             j += 1
#             assert sep_t not in target[j].lower(), target[j]
#         assert 0
#     assert len(src) == len(target), (i, len(src), len(target))
#     print((len(src), len(target)))    
#     srcs += src
#     targets += target
# assert len(srcs) == len(targets)



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
if to_txt:
    print('Generating txt...')
    result = []
    for src, target in zip(srcs, targets):
        #result.append('$ %s' % src)
        line = src + '>>>>' + target
        result.append(line)
        # result.append('_ %s' % target)
    
    result = '\n\n'.join(result)

else:
    print("Generating latex code...")
    def text_to_latex(text):
        code = unicode_to_latex(text)
        #code = '*UnicodeEncodeError*'
        return code
    result = latex_templates.get_latex_start(title = title,
                                             author = author)
    result += text_to_latex(srcs[0]) + '\n\\switchcolumn\n' + text_to_latex(targets[0])
    
    
    for i in range(1, min(len(srcs), len(targets))):
        if i > 4000:
            break
        src_t = text_to_latex(srcs[i])
        targt_t = text_to_latex(targets[i])
        result += '\n\\switchcolumn*\n' + src_t + '\n\\switchcolumn\n' + targt_t
        
    result += latex_templates.get_latex_end()
name = '%s.txt' % title.replace(' ', '_')
filepath = os.path.join(r'C:\Users\gcvic\Documents\bilingual-document-generator\%s' % name)
with open(filepath, 'w', encoding='utf8') as fp:
    fp.write(result)
print("Goed gedaan!", filepath)
    

    #target = re.split(r'#\s*t[o|u]ken\s*#', translations[i], flags = re.IGNORECASE)
    #target = re.split(r'token|tuken', translations[i], flags = re.IGNORECASE)