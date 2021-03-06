# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 19:17:49 2020

@author: gcvic
"""




from tika import parser
from pylatexenc.latexencode import unicode_to_latex
import pandas as pd
import os
import googletrans
import latex_templates
from emoji import  demojize
from matplotlib import pyplot as plt
import nltk
from googletrans import Translator
from collections import defaultdict
from mtranslate import translate
import tqdm
import random
import time
import re


debug = 0
filename = 'La_Lotteria_di_Shirley_Jackson'
title = 'La Lotteria'
author = 'Shirley Jackson'
source_lang = 'it'
target_lang = 'es'
tokenizer_lang = 'italian'



random.seed(7)
pdf_path = r'C:\Users\gcvic\Documents\bilingual-document-generator\%s.pdf'\
    % filename
print("Reading text from %s..." % pdf_path)
raw = parser.from_file(pdf_path)
raw = raw['content']#.encode('utf-8', errors='ignore')
raw = str(raw).replace("\n", "").replace("\\", "")
print("%d characters read" % len(raw))

# AD-hoc transformation
# raw = raw.replace('[', '').replace(']', '')



tokenizer_path = 'tokenizers/punkt/%s.pickle' % tokenizer_lang
print('Tokenizing with %s...' % tokenizer_path)
tokenizer = nltk.data.load(tokenizer_path)
tokens = tokenizer.tokenize(raw)
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
print('PLotting...')
plt.figure()
pd.Series([len(t) for t in tokens]).plot.hist(bins = 200, title = 'Token length')
plt.show()
sep = ' #TOKEN# '

chunks = []
max_chunksize = 10000
chunk = []
for token in tqdm.tqdm(tokens, desc = 'Creating chunks'):
    if (len(sep) * len(chunk)+sum([len(t) for t in chunk + [token]])) < max_chunksize:
        chunk.append(token)
    else:
        if len(chunk) > 0:
            chunks.append(sep.join(chunk))
        chunk = []
chunks.append(sep.join(chunk))
print('Plotting')
plt.figure()
pd.Series([len(c) for c in chunks]).plot.hist(bins = 200,
                                              title = 'Chunk length')   
plt.show()

translations = defaultdict(str)

print("Translating %d..." % len(chunks))
for i, t in tqdm.tqdm(enumerate(chunks),
                      desc = 'Translating',
                      total = len(chunks)):
    if i in translations:
        continue
    demojized_token = demojize(t)
    translation = translate(demojized_token, target_lang)

    translations[i] = translation#.text
    secs = random.random() * 8
    time.sleep(secs)

srcs = []
targets = []
sep_t = 'TOKEN' #regexPattern = '|'.join(['-_._-'])
for i in tqdm.tqdm(range(len(chunks)),
                   desc = 'Creating columns...'):
    src = chunks[i].split(sep)
    target = translations[i].split(sep_t)
    
    assert len(src) == len(target), (i, len(src), len(target))
    if not len(src) == len(target):
        pass
    print((len(src), len(target)))
        
    srcs += src
    targets += target
assert len(srcs) == len(targets)
def lreplace(pattern, sub, string):
    return re.sub('^%s' % pattern, sub, string)

def rreplace(pattern, sub, string):
    return re.sub('%s$' % pattern, sub, string)
print('Replacing artifacts...')
targets = [t.replace(' #', '').replace('# ', '').strip()\
           for t in tqdm.tqdm(targets)]



print("Generating latex code...")
def text_to_latex(text):
    code = unicode_to_latex(text)
    #code = '*UnicodeEncodeError*'
    return code
result = latex_templates.get_latex_start(title = title,
                                         author = author)
result += text_to_latex(srcs[0]) + '\n\\switchcolumn\n' + text_to_latex(targets[0])


for i in range(1, min(len(srcs), len(targets))):
    src_t = text_to_latex(srcs[i])
    targt_t = text_to_latex(targets[i])
    result += '\n\\switchcolumn*\n' + src_t + '\n\\switchcolumn\n' + targt_t
    
result += latex_templates.get_latex_end()
filepath = os.path.join(r'C:\Users\gcvic\Documents\bilingual-document-generator\code.txt')
with open(filepath, 'w', encoding='utf8') as fp:
    fp.write(result)
print("Goed gedaan!", filepath)
    