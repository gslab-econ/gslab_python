#! /usr/bin/env python
'''
#################################################################
#  tablefill_readme.txt - Help/Documentation for tablefill.py
#################################################################

Description:
tablefill.py is a Python module designed to fill LyX tables with output from text files (usually output from Stata or Matlab).

Usage:
Tablefill takes as input a LyX file containing empty tables (the template file) and text files containing data to be copied to 
these tables (the input files), and produces a LyX file with filled tables (the output file). 

Tablefill must first be imported to make.py.  This is typically achieved by including the following lines:

```
from gslab_fill.tablefill import tablefill
```

Once the module has been imported, the syntax used to call tablefill is as follows:

```
tablefill( input = 'input_file(s)', template = 'template_file', output = 'output_file' )
```

The argument 'template' is the user written LyX file which contains the tables to be filled in. The argument 'input' is a list of 
the text files containing the output to be copied to the LyX tables. If there are multiple input text files, they are listed as: 
input = 'input_file_1 input_file_2'. The argument 'output' is the name of the filled LyX file to be produced.  Note that this file
is created by tablefill.py and should not be edited manually by the user.

For an example of this syntax in use, please see make.py in the svn_drafts template directory at /admin/Templates/svn_drafts/.
###########################
Input File Format:
###########################

The data needs to be tab-delimited rows of numbers (or characters), preceeded by `<label>`.  The < and > are mandatory.
The numbers can be arbitrarily long, can be negative, and can also be in scientific notation.

Examples:
----------

```
<tab:Test>
1   2   3
2   3   1
3   1   2
```

```
<tab:FunnyMat>
1   2   3   23  2
2   3
3   1   2   2
1
```
(The rows do not need to be of equal length.)

Completely blank (no tab) lines are ignored.
If a "cell" is merely "." or "[space]", then it is treated as completely missing.
That is, in the program:

```
<tab:Test>
1   2   3
2   .   1   3
3       1   2
```

is equivalent to:
```
<tab:Test>
1   2   3
2   1   3
3   1   2
```

This feature is useful as Stata outputs missing values in numerical variables as ".", and missing values in string variables
as "[space]".

................................
 Scientific Notation Notes:
................................
The scientific notation ihas to be of the form:
[numbers].[numbers]e(+/-)[numbers]

Examples:
```
23.2389e+23
-2.23e-2
-0.922e+3
```

###########################
Template LyX Format:
###########################

The LyX template file determines where the numbers from the input files are placed.

Every table in the template file (if it is to be filled) must appear within a float. There must be one, and only one, table object inside the float,
and the table name must include a label object that corresponds to the label of the required table in the input file.

Note that table names cannot be duplicated.  For a single template file, each table to be filled must have a unique label, and there must be one,
and only one, table with that same label in the text files used as input. Having multiple tables with the same name in the input files or in the 
template file will cause errors.  

Note also that labels are NOT case-sensitive. That is, <TAB:Table1> is considered the same as `<tab:table1>`.

In the LyX tables, "cells" to be filled with entries from the input text files are indicated by the following tags:
`"###"  (no quotes)`
or 
`"#[number][,]#"  (no quotes)`

The first case will result in a literal substitution.  I.e. whatever is in the text tables for that cell will be copied over.
The second case will convert the data table's number (if in scientific notation) and will truncate this converted number 
to [number] decimal places.  It will automatically round while doing so.

If a comma appears after the number (within #[number]#), then it will add commas to the digits to the left of the decimal place.

Examples:
---------
```
2309.2093 + ### = 2309.2093
2309.2093 + #4# = 2309.2093
2309.2093 + #5# = 2309.20930
2309.2093 + #20# = 2309.20930000000000000000
2309.2093 + #3# = 2309.209
2309.2093 + #2# = 2309.21
2309.2093 + #0# = 2309
2309.2093 + #0,# = 2,309
```

```
-2.23e-2  + #2# = -0.0223 + #2# = -0.02
-2.23e-2  + #7# = -0.0223 + #7# = -0.0223000
-2.23e+10  + #7,# = -22300000000 + #7,# = -22,300,000,000.000000
```

Furthermore, only ###/#num# will be replaced, allowing you to put things around ###/#num# to alter the final output:

Examples:
--------

```
2309.2093 + (#2#) = (2309.21)
2309.2093 + #2#** = 2309.21**
2309.2093 + ab#2#cd = ab2309.21cd
```

If you are doing exact substitution, then you can use characters:

Examples:
---------
`abc + ### = abc`

................................
 Intentionally blank cells:
................................

If you would like to display a blank cell, you can use "---":

Examples:
---------
```
--- + ### = ---
--- + #3# = ---
```

######################
# Example Combinations 
#   Of input + template
######################


Example 1 (Simple)
----------
```
Input: <tab:Test>
1   2   3
2   1   3
3   1   2

Template: `<tab:Test> ` (pretend this is what you see in LyX)

### ### ###
### ### ###
### ### ###

Result:<tab:Test>
1   2   3
2   1   3
3   1   2
```



Example 2 (More Complicated)
----------
```
Input: <tab:Test>
1   .   3
2e-5    1   3.023
.   -1  2   3

Template: <tab:Test>  (pretend this is what you see in LyX)
(###)   2   ###
#3# ### #1#
NA  ### ### ###

Result:<tab:Test>
(1) 2   3
0.000   1   3.0
NA  -1  2   3
```


===================
====Important======
===================
By design, missings in input table and "missings" in template do not have to line up.

Example 3 (LyX)
----------
```
Input: <tab:Test>
1   .   3
2e-5    .   3.023
.   -1  2

Template: <tab:Test> 
### ### abc
abc #2# #3#
NA  ### ###

Result:<tab:Test>
1   3   abc
abc 0.00    3.023
NA  -1  2

Recall that to the program, the above input table is no different from:
1   3
2e-5    3.023
-1  2
```

It doesn't "know" where the numbers should be placed within a row, only what the next number to place should be.

Similarly:

Example 4 (LyX)
----------
```
Input: <tab:Test>
1   1   2
1   1   3
2   -1  2

Template: <tab:Test>  
### ### ###
abc abc abc
### #2# #3#
### ### ###

Result:<tab:Test>
1   1   2
abc abc abc
1   1.00    3.000
2   -1  2
```

If a row in the template has no substitutions, then it's not really a row from the program's point of view.


######################
# Error Logging
######################

If an error occurs during the call to tablefill, it will be displayed in the command window.  When make.py finishes, the user will
be able to scroll up through the output and examine any error messages.  Error messages, which include a description of the error type
and a traceback to the line of code where the error occured, can also be retuned as a string object using the following syntax:

exitmessage = tablefill( input = 'input_file(s)', template = 'template_file', output = 'output_file' )

Lines can then be added to make.py to output this string to a log file using standard python and built in gslab_make commands.


######################
# Common Errors
######################

Common mistakes which can lead to errors include:

- Mismatch between the length of the LyX table and the corresponding text table.  If the lyx table has more entries to be filled than the
text table has entries to fill from, this will cause an error and the table will not be filled.

- Use of numerical tags (e.g. #1#) to fill non-numerical data.  This will cause an error. Non-numerical data can only be filled using "###",
as it does not make sense to round or truncate this data.

- Multiple table objects in the same float.  Each table float in the template LyX file can only contain one table object.  If a float contains
a second table object, this table will not be filled.


######################
# Boldfacing entries
######################

It is straightforward to develop functions that conditionally write entries of tables in boldface; functions may do so by inserting
'\series bold' in the lines of the filled LyX file immeadiately before phrases that the user wishes to make bold. An example of this
procedure is implemented by the code contained in /source/analysis/tables104th of the politext project repository
(Tree: a62cee7bb80d27a516439a7c745786d8fa4aec8a).
'''

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
    
