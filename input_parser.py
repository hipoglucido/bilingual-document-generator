from tika import parser

import pandas as pd
import os

from emoji import  demojize
import nltk
from googletrans import Translator
from collections import defaultdict
from mtranslate import translate
import tqdm
import random
import time
import re
import pickle

def read_pdf(filepath):
    print("Reading %s...." % filepath)
    raw = parser.from_file(filepath)
    safe_text = raw['content']#.encode('utf-8', errors='ignore')
    safe_text = str(safe_text).replace("\n", "").replace("\\", "")
    return safe_text
    
def get_raw_text() -> str:
    print("Reading text...")
    folder = r'C:\Users\gcvic\Documents\bilingual-document-generator'
    raw = parser.from_file(os.path.join(folder, r"Dahl, Roald - Le Streghe.pdf"))
    safe_text = raw['content']#.encode('utf-8', errors='ignore')
    safe_text = str(safe_text).replace("\n", "").replace("\\", "")
    return safe_text

filepath = r'C:\Users\gcvic\Documents\bilingual-document-generator\ORWELL-la_fattoria_degli_animali.pdf'
s = read_pdf(filepath)
