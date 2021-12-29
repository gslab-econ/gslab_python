# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 05:44:33 2021

@author: user
"""

import pandas as pd
import hashlib
import sys

pd.set_option('display.float_format', lambda x: '%.5f' % x)

def SaveData(df, keys, out_file, log_file):
    CheckKeys(df, keys)
    df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest() 
    summary_stats = GetSummaryStats(df)
    SaveDf(df, out_file)
    SaveLog(df_hash, keys, summary_stats, out_file, log_file)
    
def CheckKeys(df, keys):
    df_keys = df[keys]
    key_counts = df_keys.value_counts()
    if not all(x == 1 for x in key_counts):
        print("Keys do not uniquely identify the observations")
        sys.exit()
        
def GetSummaryStats(df):
    var_types = df.dtypes
    var_stats = df.describe().transpose()
    summary_stats = pd.DataFrame({'type': var_types}).\
        merge(var_stats, how = 'left', left_index = True, right_index = True)
    summary_stats = summary_stats.round(4)
    return(summary_stats)    

def SaveDf(df, out_file):
    df.to_csv(out_file, index = False)
    
def SaveLog(df_hash, keys, summary_stats, out_file, log_file):
    with open(log_file, 'w') as f:
        f.write(f'File: {out_file}\n\n')
        f.write(f'MD5 hash: {df_hash}\n\n')
        f.write('Keys: ')
        for item in keys:
            f.write(f'{item} ')
        f.write('\n\n')
        f.write(summary_stats.to_string(header = True, index = True))
        f.write("\n")
        
    f.close()

