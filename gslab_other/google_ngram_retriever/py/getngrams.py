#!/usr/bin/env python
# -*- coding: utf-8 -*
from ast import literal_eval
from pandas import DataFrame  # http://github.com/pydata/pandas
import re
import requests               # http://github.com/kennethreitz/requests
import subprocess
import sys
import os

def downloadGoogleNgrams(query, saveFolder = './', filename = '', corpus = 'eng_2012', startYear = 1800, endYear = 2000, smoothing = 3, caseInsensitive = True, allData = True):
    if '*' in query and caseInsensitive is True:
        caseInsensitive = False
        notifyUser = True
        warningMessage = "*NOTE: Wildcard and case-insensitive " + \
                        "searches can't be combined, so the " + \
                        "case-insensitive option was ignored."
    elif '_INF' in query and caseInsensitive is True:
        caseInsensitive = False
        notifyUser = True
        warningMessage = "*NOTE: Inflected form and case-insensitive " + \
                         "searches can't be combined, so the " + \
                         "case-insensitive option was ignored."
    else:
        notifyUser = False
        url, urlquery, df = getNgrams(query, corpus, startYear, endYear,
                                      smoothing, caseInsensitive)
    if not allData:
        if caseInsensitive is True:
            for col in df.columns:
                if col.count('(All)') == 1:
                    df[col.replace(' (All)', '')] = df.pop(col)
                elif col.count(':chi_') == 1 or corpus.startswith('chi_'):
                    pass
                elif col.count(':ger_') == 1 or corpus.startswith('ger_'):
                    pass
                elif col.count(':heb_') == 1 or corpus.startswith('heb_'):
                    pass
                elif col.count('(All)') == 0 and col != 'year':
                    if col not in urlquery.split(','):
                        df.pop(col)
        if '_INF' in query:
            for col in df.columns:
                if '_INF' in col:
                    df.pop(col)
        if '*' in query:
            for col in df.columns:
                if '*' in col:
                    df.pop(col)
    queries = ''.join(urlquery.replace(',', '_').split())
    if '*' in queries:
        queries = queries.replace('*', 'WILDCARD')
    if caseInsensitive is True:
        word_case = 'caseInsensitive'
    else:
        word_case = 'caseSensitive'

    if len(filename) == 0:
        filename = '%s-%s-%d-%d-%d-%s.csv' % (queries, corpus, startYear,
                                              endYear, smoothing, word_case)
    if not filename.lower().endswith('.csv'):
        filename = filename + '.csv'
    for col in df.columns:
        if '&gt;' in col:
            df[col.replace('&gt;', '>')] = df.pop(col)
    df.to_csv(os.path.join(saveFolder, filename), index=False)
    print(('Data saved to %s' % os.path.join(saveFolder, filename)))
    if notifyUser:
        print(warningMessage)
            
            
def getNgrams(query, corpus, startYear, endYear, smoothing, caseInsensitive):
    corpora = dict(eng_us_2012=17, eng_us_2009=5, eng_gb_2012=18, eng_gb_2009=6,
               chi_sim_2012=23, chi_sim_2009=11, eng_2012=15, eng_2009=0,
               eng_fiction_2012=16, eng_fiction_2009=4, eng_1m_2009=1,
               fre_2012=19, fre_2009=7, ger_2012=20, ger_2009=8, heb_2012=24,
               heb_2009=9, spa_2012=21, spa_2009=10, rus_2012=25, rus_2009=12,
               ita_2012=22)
               
    params = dict(content=query, year_start=startYear, year_end=endYear,
                  corpus=corpora[corpus], smoothing=smoothing,
                  case_insensitive=caseInsensitive)
    if params['case_insensitive'] is False:
        params.pop('case_insensitive')
    if '?' in params['content']:
        params['content'] = params['content'].replace('?', '*')
    if '@' in params['content']:
        params['content'] = params['content'].replace('@', '=>')
    req = requests.get('http://books.google.com/ngrams/graph', params=params)
    res = re.findall('var data = (.*?);\\n', req.text)
    if res:
        data = {qry['ngram']: qry['timeseries']
                for qry in literal_eval(res[0])}
        df = DataFrame(data)
        df.insert(0, 'year', list(range(startYear, endYear + 1)))
    else:
        df = DataFrame()
    return req.url, params['content'], df




