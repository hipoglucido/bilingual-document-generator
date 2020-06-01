

from tika import parser
from pylatexenc.latexencode import unicode_to_latex
import pandas as pd
import os
import googletrans
import latex_templates
from emoji import  demojize
import nltk
from googletrans import Translator
from collections import defaultdict
import tqdm
import random
import time
import re
def get_raw_text() -> str:
    print("Reading text...")
    folder = r'C:\Users\gcvic\Documents\bilingual-document-generator'
    raw = parser.from_file(os.path.join(folder, r"Dahl, Roald - Le Streghe.pdf"))
    safe_text = raw['content']#.encode('utf-8', errors='ignore')
    safe_text = str(safe_text).replace("\n", "").replace("\\", "")
    return safe_text

def translate_text(text, source_lang, target_lang) -> str:
    return

def text_to_latex(text):
    code = unicode_to_latex(text)
    return code

source_lang = 'it'
target_lang = 'es'
raw = get_raw_text()
# translation = translate_text(text = raw,
#                              source_lang = source_lang,
#                              target_lang = target_lang)


tokenizer = nltk.data.load('tokenizers/punkt/italian.pickle')
tokens = tokenizer.tokenize(raw)
def parse_token(t):
    t = re.sub(r'\.{3,}', "...", t)
    return t
print("Parsing tokens...")
tokens = [parse_token(t) for t in tokens]
pd.Series([len(t) for t in tokens]).plot.hist(bins = 200,logx = True)

for token in tokens:
    if len(token) > 100:
        break
bt = [t for t in tokens if len(t) > 400]
translations = defaultdict(str)


print("translating %d..." % len(tokens))
for i, t in tqdm.tqdm(enumerate(tokens), desc = 'Translating sentences', total = len(tokens)):
    if i in translations:
        continue
    demojized_token = demojize(t)
    translator = Translator()
    translation = translator.translate(demojized_token, dest = target_lang, src = source_lang)
    translations[i] = translation.text
    secs = random.random() * 2
    time.sleep(secs)
    
# demojized_tokens = [demojize(t) for t in tokens]
# trans_tokens = translator.translate(demojized_tokens, dest = target_lang, src = source_lang)
# pd.Series([len(t) for t in trans_tokens]).plot.hist(bins = 100)

print("Generating latex code...")
result = latex_templates.get_latex_start(title = 'Le streghe',
                                         author = 'Roald Dahl')
result += text_to_latex(tokens[0]) + '\n\\switchcolumn\n' + text_to_latex(translations[0])
for i in range(1, min(len(tokens), len(translations.keys()))):
    src_t = text_to_latex(tokens[i])
    targt_t = text_to_latex(translations[i])
    result += '\n\\switchcolumn*\n' + src_t + '\n\\switchcolumn\n' + targt_t
    
result += latex_templates.get_latex_end()
filepath = os.path.join(r'C:\Users\gcvic\Documents\bilingual-document-generator\code.txt')
with open(filepath, 'w') as fp:
    fp.write(result)
    
    