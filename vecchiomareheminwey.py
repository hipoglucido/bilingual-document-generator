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
import pickle

pdf_path = r'C:\Users\gcvic\Documents\bilingual-document-generator\Hvecchiomare.pdf'



source_lang = 'it'
target_lang = 'es'
print("Reading text...")
   
raw = parser.from_file(pdf_path)
raw = raw['content']#.encode('utf-8', errors='ignore')
raw = str(raw).replace("\n", "").replace("\\", "")


# AD-hoc transformation
raw = raw.replace('[', '').replace(']', '')
# caps = ['Capitolo %s' % s for s in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']]
# for cap in caps:
#     assert cap in raw
#     s = '\n%s\n' % cap
#     raw = raw.replace(cap, s, 1)



tokenizer = nltk.data.load('tokenizers/punkt/italian.pickle')
tokens = tokenizer.tokenize(raw)
def parse_token(t):
    t = re.sub(r'\.{3,}', "...", t)
    return t
print("Parsing tokens...")
tokens = [parse_token(t) for t in tokens]
pd.Series([len(t) for t in tokens]).plot.hist(bins = 200,logx = False)
plt.show()
sep = ' #TOKEN# '

chunks = []
max_chunksize = 10000
chunk = []
for token in tokens:
    if (len(sep) * len(chunk)+sum([len(t) for t in chunk + [token]])) < max_chunksize:
        chunk.append(token)
    else:
        if len(chunk) > 0:
            chunks.append(sep.join(chunk))
        chunk = []
chunks.append(sep.join(chunk))
pd.Series([len(c) for c in chunks]).plot.hist(bins = 200)   
plt.show()

translations = defaultdict(str)

print("translating %d..." % len(chunks))
for i, t in tqdm.tqdm(enumerate(chunks), desc = 'Translating sentences',
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
for i in range(len(chunks)):
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
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def rreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' ends 'string'.
    """
    return re.sub('%s$' % pattern, sub, string)
targets = [t.replace(' #', '').replace('# ', '').strip() for t in targets]

# for j in range(1000):
#     print('_________________________')
#     print(src[j])
#     print(target[j])
#     if '#' in target[j]:
#         break


print("Generating latex code...")
def text_to_latex(text):
    code = unicode_to_latex(text)
    #code = '*UnicodeEncodeError*'
    return code
result = latex_templates.get_latex_start(title = 'la fattoria degli animali',
                                         author = 'Orwell')
result += text_to_latex(srcs[0]) + '\n\\switchcolumn\n' + text_to_latex(targets[0])


for i in range(1, min(len(srcs), len(targets))):
    src_t = text_to_latex(srcs[i])
    targt_t = text_to_latex(targets[i])
    result += '\n\\switchcolumn*\n' + src_t + '\n\\switchcolumn\n' + targt_t
    
result += latex_templates.get_latex_end()
filepath = os.path.join(r'C:\Users\gcvic\Documents\bilingual-document-generator\code.txt')
with open(filepath, 'w', encoding='utf8') as fp:
    fp.write(result)
    
    