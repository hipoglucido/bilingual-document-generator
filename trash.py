# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 19:59:42 2020

@author: gcvic
"""


    # while True:
        
    #     proxies = {
    #     'http': 'http://%s' % proxy,
    #     'https': 'https://%s' % proxy}
    #     translator = Translator(proxies=proxies)
    #     try:
    #         translation = translator.translate(demojized_token,
    #                                        dest = target_lang,
    #                                        src = source_lang)
    #         print(proxy, " worked")
    #         break
    #     except Exception as e:
    #         print(str(e))
    #         proxy = random.choice(all_proxies)
    #         print("next is ", proxy)
    #         pass

# demojized_tokens = [demojize(t) for t in tokens]
# trans_tokens = translator.translate(demojized_tokens, dest = target_lang,
# src = source_lang)
# pd.Series([len(t) for t in trans_tokens]).plot.hist(bins = 100)



for token in tokens:
    if len(token) > 100:
        break
bt = [t for t in tokens if len(t) > 400]



all_proxies = list(pd.read_csv(r'C:\Users\gcvic\Downloads\http_proxies.txt', header = None)[0])
proxy = random.choice(all_proxies)