import pyodbc
import re
import numpy as np
import pandas as pd
from sql_exceptions import *

def save_table(table, key, cxn_string, **kwargs):
    kwargs['table'] = table
    kwargs['key'] = key
    kwargs['cxn_string'] = cxn_string
    checked_args = set_default_args(kwargs)

    if not checked_args['stats_only']:
        build_index(checked_args['table'],
                    checked_args['cxn_string'],
                    checked_args['key'],
                    checked_args['key_name'],
                    checked_args['index_options'])

    column_attrs = fetch_column_attrs(checked_args['table'], 
                                      checked_args['cxn_string'])

    table_stats = get_table_stats(checked_args['table'], 
                                  checked_args['cxn_string'], 
                                  column_attrs)

    table_str = table_stats.to_string(index=False)
    header = "="*100+'\n' + "Table: {}\n".format(checked_args['table']) +  \
             "Key: "+' '.join(checked_args['key'])+'\n' + "="*100+'\n'
    print header
    print table_str + '\n\n'

    if checked_args['log'] is not None:
        with open(checked_args['log'], mode = checked_args['mode']) as logfh:
            logfh.write(header)
            logfh.write(table_str + '\n\n')

    return table_stats

def set_default_args(kwargs):
    if 'log' not in kwargs:
        kwargs['log'] = '../output/data_file_manifest.log'
    if (type(kwargs['key']) is str):
        kwargs['key'] = [kwargs['key']]
    if (type(kwargs['key']) is not list):
        raise TypeError("Key must be a string or list of strings")
    if 'key_name' not in kwargs:
        kwargs['key_name'] = 'pk_{}'.format(kwargs['table'])
    if 'compress' not in kwargs:
        kwargs['compress'] = len(kwargs['key']) > 1
    if 'stats_only' not in kwargs:
        kwargs['stats_only'] = False
    if 'mode' not in kwargs:
        kwargs['mode'] = 'ab'
    if 'index_options' not in kwargs:
        kwargs['index_options'] = 'COMPRESS ADVANCED LOW PARALLEL' if (kwargs['compress']) else ''
    return kwargs    

def build_index(table, cxn_string, key, key_name, index_options):
    cxn = pyodbc.connect(cxn_string)
    cursor = cxn.cursor()

    key_str = ', '.join(key)
    stmt = ("ALTER TABLE {table} ADD CONSTRAINT {key_name} "
            "PRIMARY KEY ({key_str}) DISABLE").format(table = table,
                                                      key_name = key_name,
                                                      key_str  = key_str)
    cursor.execute(stmt)
    cursor.commit()

    stmt = ("CREATE UNIQUE INDEX {key_name} ON {table} ({key_str}) "
            "{index_options}").format(table = table,
                                      key_name = key_name,
                                      key_str  = key_str,
                                      index_options = index_options)
    cursor.execute(stmt)
    cursor.commit()

    stmt = 'ALTER TABLE {} ENABLE PRIMARY KEY'.format(table)
    cursor.execute(stmt)
    cursor.commit()
    cxn.close()

def fetch_column_attrs(table, cxn_string):
    cxn = pyodbc.connect(cxn_string)
    cursor = cxn.cursor()
    query = ("SELECT column_name, data_type FROM user_tab_cols "
             "WHERE table_name = '{}'").format(table.upper())
    cursor.execute(query)
    attrs = cursor.fetchall()
    cxn.close()

    return attrs

def get_table_stats(table, cxn_string, attrs):
    queries = [build_stats_query(colname, dtype) for (colname, dtype) in attrs]
    query = 'SELECT ' + ', '.join(queries) + ' FROM {tab}'.format(tab = table)
    query = query.replace('\n','')
    query = ' '.join(query.split())

    cxn = pyodbc.connect(cxn_string)
    cursor = cxn.cursor()
    cursor.execute(query)
    statsnames = [column[0] for column in cursor.description]
    result = cursor.fetchall()
    cxn.close()

    stats = zip(statsnames, result[0])
    stats_table = build_stats_table(attrs, stats)

    return stats_table

def build_stats_query(colname, dtype):
    if (dtype == 'NUMBER' or dtype == 'LONG'):
        query = """
                COUNT({col}), AVG({col}), STDDEV({col}), MIN({col}), MAX({col})
                """.format(col=colname)
    elif (dtype == 'DATE'):
        query = 'COUNT({col}), MIN({col}), MAX({col})'.format(col=colname)
    else:
        query = 'COUNT({col})'.format(col=colname)
    return query

def build_stats_table(column_attrs, stats):
    colnames = map(lambda x: x[0], column_attrs)
    stats_frame = pd.DataFrame(data = colnames, columns = ['Variable'])

    stats_types = ['COUNT','AVG','STDDEV','MIN','MAX']
    for stype in stats_types:
        relevant_stats = filter(lambda x: stype == x[0][:len(stype)], stats)
        colnames   = map(lambda x: re.search('\((.*)\)', x[0]).group(1), relevant_stats)
        stat_value = map(lambda x: x[1], relevant_stats)
        temp_frame = pd.DataFrame(data = {'Variable' : colnames, stype : stat_value})
        stats_frame = stats_frame.merge(
                          right = temp_frame, 
                          on = 'Variable',
                          how = 'left')
    stats_frame = stats_frame.sort(columns = 'Variable', axis = 0)
    return stats_frame