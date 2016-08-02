#! /usr/bin/env python
#**************************************************************************
# Tablefill.py - Fills tagged tables in LyX Files with external text tables
#**************************************************************************

import os, argparse, types, re, traceback
from decimal import Decimal, ROUND_HALF_UP

def tablefill(**kwargs):
    try:
        args = parse_arguments(kwargs)
        tables = parse_tables(args)
        lyx_text = insert_tables(args, tables)
        lyx_text = insert_warning(args, lyx_text)
        write_to_lyx(args, lyx_text)
        exitmessage = args['template'] + ' filled successfully by tablefill'
        print exitmessage
        return exitmessage	
    except:
        print 'Error Found'
        exitmessage = traceback.format_exc()
        print exitmessage
        return exitmessage
    
def parse_arguments(kwargs):
    args = dict()
    if 'input' in kwargs.keys():
        input_list = kwargs['input'].split()
        args['input'] = input_list
    if 'template' in kwargs.keys():
        args['template'] = kwargs['template']
    if 'output' in kwargs.keys():
        args['output'] = kwargs['output']        
    
    return args

def parse_tables(args):
    data = read_data(args['input'])
    tables = parse_data(data)
    
    return tables

def read_data(input):
    data = []
    if isinstance(input, types.StringTypes):
        input = [input]
    for file in input:
        data += open(file, 'rU').readlines()
    
    return data

def parse_data(data):
    tables = {}
    for row in data:
        if re.match('^<Tab:', row, flags = re.IGNORECASE):
            tag = re.sub('<Tab:', '', row, flags = re.IGNORECASE)
            tag = re.sub('>\n', '', tag, flags = re.IGNORECASE)
            tag = tag.lower()
            tables[tag] = []
        else:
            clean_row = row.strip()
            tables[tag] = tables[tag] + clean_row.split('\t')
    for table_tag in tables:
        for n in range( len(tables[table_tag]) ):
            clean_entry = tables[table_tag][n].strip()
            tables[table_tag][n] = clean_entry
        tables[table_tag] = filter(lambda a: a != '.' and a != '', tables[table_tag])
        
    return tables    
    
def insert_tables(args,tables):
    lyx_text = open(args['template'], 'rU').readlines()
    for n in range( len(lyx_text) ):
        if lyx_text[n].startswith('name "tab:'):
            tag = lyx_text[n].replace('name "tab:','').rstrip('"\n').lower()
            if tag in tables:
                i = n
                entry_count = 0
                search_table = True
                
                while search_table is True:
                    i+=1
                    
                    if re.match('^.*###', lyx_text[i]):
                        lyx_text[i] = lyx_text[i].replace('###', tables[tag][entry_count])
                        entry_count+=1
                        
                    elif re.match('^.*#\d+#', lyx_text[i]) or re.match('^.*#\d+,#', lyx_text[i]):
                        entry_tag = re.split('#', lyx_text[i])[1]
                        if re.match('---', tables[tag][entry_count]):
                            rounded_entry = '---'
                        else:
                            rounded_entry = round_entry(entry_tag, tables[tag][entry_count])
                            if re.match('^.*#\d+,#', lyx_text[i]):
                                rounded_entry = insert_commas(rounded_entry)
                        lyx_text[i] = lyx_text[i].replace('#' + entry_tag + '#', rounded_entry)
                        entry_count+=1
                        
                    elif lyx_text[i]=='</lyxtabular>\n':
                        search_table = False
    
    return lyx_text
    
def round_entry(entry_tag, entry):
    round_to = int(entry_tag.replace(',', ''))
    decimal_place = round(pow(0.1, round_to), round_to)
    if round_to == 0:
        decimal_place = str(int(decimal_place))
    else:
        decimal_place = str(decimal_place)
    rounded_entry = str(Decimal(entry).quantize(Decimal(decimal_place), rounding = ROUND_HALF_UP))

    return rounded_entry

def insert_commas(entry):
    integer_part = re.split('\.', entry)[0]
    integer_part = format(int(integer_part), ',d')
    
    if re.search('\.', entry):
        decimal_part = re.split('\.', entry)[1]
        entry_commas = integer_part + '.' + decimal_part 
    else:
        entry_commas = integer_part

    if float(entry) < 0 and entry_commas[0] != '-':
        entry_commas = '-' + entry_commas
    
    return entry_commas
    
def insert_warning(args, lyx_text):
    input = ' '.join(args['input'])
    template = ''.join(args['template'])
    message = '\n\\begin_layout Standard\n\\begin_inset Note Note\nstatus open' \
               '\n\n\\begin_layout Plain Layout\nThis file was produced by ' \
               'tablefill.py from template file %s and input file(s) %s.  To make '\
               'changes in this file, edit the input and template files. Do not '\
               'edit this file directly.\n\\end_layout\n\n\\end_inset\n\n\\end_layout\n'
    filled_message = message % (template, input)
    message_lines = filled_message.split('\n')
    message_lines = [s + '\n' for s in message_lines]
    printed = False
    n = -1
    while not printed:
        n += 1
        if lyx_text[n].startswith('\\begin_body'):
            lyx_text[n+1:n+1] = message_lines
            printed = True
        
    return lyx_text
    
def write_to_lyx(args, lyx_text):    
    outfile = open(args['output'], 'wb')
    outfile.write( ''.join(lyx_text) )
    outfile.close()
    
