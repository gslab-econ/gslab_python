#! /usr/bin/env python
'''
#################################################################
#  textfill_readme.txt - Help/Documentation for textfill.py
#################################################################

Description:
textfill.py is a python module designed to copy sections of log files produced by Stata to LyX files.

Usage:
Textfill takes as input log files produced by Stata (the input files) and a LyX file with labels indicating where logs should be 
inserted (the template file), and produces a LyX file (the output file) which includes sections of the input files (as indicated by 
tags inside the input files) in the locations indicated by the labels in the template file.

Textfill must first be imported to make.py.  This is typically achieved by including the following lines:

```
sys.path.append('./external/lib/python/')
from gslab_misc.py.textfill import textfill
```

In the above example, the gslab_misc library has been added to the ./external/ directory by get_externals.  If the location of 
gslab_misc differs from the above, then the path must be altered accoringly.

Once the module has been imported, the syntax used to call textfill is as follows:

```
textfill( input = 'input_file(s)', template = 'template_file', output = 'output_file', [size = 'size'], [remove_echoes = 'True/False'] )
```

The argument 'input' is a list of the text files containing the stata logs to be copied to the LyX tables. If there are multiple input 
text files, they are listed as: input = 'input_file_1 input_file_2'. The argument 'template' is the user written LyX file which contains 
the labels which will be replaced with sections of the log files. The argument 'output' is the name of the filled LyX file to be produced.
Note that this file is created by textfill.py, and should not be edited manually by the user.

There are two optional arguments: 'size' and 'remove_echoes'. The argument 'size' determines the size of inserted text relative to body text
in the output file. It accepts LaTeX font size arguments, and defaults to same size as body. The argument 'remove_echoes' determines whether
or not Stata command echoes are removed from the copied log.  It defaults to false.


###########################
Input File Format:
###########################

Input files for textfill.py are log files produced by Stata. Sections of input files to be inserted by textfill are indicated by tags printed
by the stata command 'insert_tags', which is defined by a gslab ado file in /lib/stata/gslab_misc/.

In the stata do file which produces the input logs, the user begins a tagged section with the command:
insert_tag tag_name, open

This will insert the following line, which indicates the beginning of a tagged section of the log, into the log file:
`<textfill_tag_name>`

The user should now add lines to the do file which print the output they want to add to the tagged section, followed by the line:
insert_tag tag_name, close

This inserts the following line to the log file, indicating the end of the tagged section:
`</textfill_tag_name>`


###########################
Template LyX Format:
###########################

The LyX template file contains labels which determine where the tagged sections of the input files are inserted. To insert a log section tagged as
'tag_name', in a particular place in the LyX file, the user inserts a label object with the value 'text:tag_name' inside a 'Text' custom inset.  The 'text:' part of the label
is mandatory. When textfill is run, the tagged section of the input files will be inserted as text input at the location of corresponding label 
in the LyX file.

Note that the 'Text' custom inset object is available from 'Insert > Custom Insets' when Lyx had been reconfigured with the custom module text.module.
This module is available on the repo at /admin/Computer Build Sheet/, and can be installed according to the instructions in /admin/Computer Build Sheet/standard_build.pdf.

Note that label/tag names cannot be duplicated.  For a single template file, each block of text to be inserted must have a unique label, and there 
must be one, and only one, section of the input files tagged with that same label. Having multiple sections of the input files or multiple labels in 
the template file with the same name will cause errors.  

Note also that when a LyX file with a 'text:' label is opened in LyX, or when textfill.py is run on it, LyX may issue a warning:
"The module text has been requested by this document but has not been found..."

This warning means that the custom module text.module has not been installed - see above.


#####################
# Example
#####################

The following is an example of code, which could appear in a Stata do file, used to produce input for textfill.
```
insert_tag example_log, open
display "test"
insert_tag example_log, close
```

Suppose output from Stata is being logged in stata.log.  This code adds the following lines to stata.log:

```
. insert_tag example_log, open
<example_log>

. display "test"
test

. insert_tag example_log, close
</example_log>
```

Suppose we have a LyX file, template.lyx, which contains a label with the value "text:example_log" (without the ""). The following textfill command,
`textfill( input = 'stata.log', template = 'template.lyx', output = 'output.lyx' )`

would produce a file, output.lyx, identical to template.lyx, but with the label "text:example.log" replaced with the verbatim input:

```
. display "test"
test
```

The following command,
`textfill( input = 'stata.log', template = 'template.lyx', output = 'output.lyx', remove_echoes = True )`

would produce output.lyx replacing the label with the verbatim input (removing Stata command echoes):


`test`


######################
# Error Logging
######################

If an error occurs during the call to text, it will be displayed in the command window.  When make.py finishes, the user will
be able to scroll up through the output and examine any error messages.  Error messages, which include a description of the error type
and a traceback to the line of code where the error occured, can also be retuned as a string object using the following syntax:

```
exitmessage = textfill( input = 'input_file(s)', template = 'template_file', output = 'output_file', [size = 'size'], [remove_echoes = 'True/False'] )
```

Lines can then be added to make.py to output this string to a log file using standard python and built in gslab_make commands.
'''
import os, argparse, types, traceback
from HTMLParser import HTMLParser, HTMLParseError

def textfill(**kwargs):
    try:
        args = parse_arguments(kwargs)
        text = parse_text(args)
        insert_text(args, text)
        exitmessage = args['template'] + ' filled successfully by textfill'
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
    if 'remove_echoes' in kwargs.keys():
        args['remove_echoes'] = kwargs['remove_echoes']
    else:
        args['remove_echoes'] = False
    if 'size' in kwargs.keys():
        args['size'] = kwargs['size']
    else:
        args['size'] = 'Default'
    if 'prefix' in kwargs.keys():
        args['prefix'] = kwargs['prefix'] + "_"
    else:
        args['prefix'] = 'textfill_'
    
    return args

def parse_text(args):
    text = read_text(args['input'], args['prefix'])
    text = clean_text(text, args['remove_echoes'])
    
    return text

def read_text(input, prefix):
    data = ''
    if isinstance(input, types.StringTypes):
        input = [input]
    for file in input:
        data += open(file, 'rU').read()
    text = text_parser(prefix)
    text.feed(data)
    text.close()
    
    return text

class text_parser(HTMLParser):
    def __init__(self, prefix):
        HTMLParser.__init__(self)
        self.recording = False
        self.results = {}
        self.open = []
        self.closed = []
        self.prefix = prefix
    
    def handle_starttag(self, tag, attrs):
        if tag.startswith(self.prefix):
            tag_name = tag.replace(self.prefix, '', 1)
            self.recording = True
            self.results[tag_name] = ''
            self.open.append(tag_name)
    
    def handle_data(self, data):
        if self.recording:
            self.results[self.open[-1]]+=data
    
    def handle_endtag(self, tag):
        if tag.startswith(self.prefix):
            tag_name = tag.replace(self.prefix, '', 1)
            self.open.remove(tag_name)
            self.closed.append(tag_name)
            if not self.open:
                self.recording = False
    
    def close(self):
        for tag in self.results.keys():
            if tag not in self.closed:
                raise HTMLParseError('Tag %s is not closed' % tag)

def clean_text(text, remove_echoes):
    for key in text.results:
        data = text.results[key].split('\n')
        if remove_echoes:
            data = filter(lambda x: not x.startswith('.'), data)
        else:
            data = filter(lambda x: not x.startswith('. insert_tag'), data)
        data = remove_trailing_leading_blanklines(data)
        text.results[key] = '\n'.join(data)
    
    return text

def remove_trailing_leading_blanklines(list):
    while list and not list[0]:
        del list[0]
    while list and not list[-1]:
        del list[-1]
    
    return list

def insert_text(args,text):
    lyx_text = open(args['template'], 'rU').readlines()
    # Loop over (expanding) raw LyX text
    n = 0
    loop = True
    while loop==True:
        n+=1 
        if n<len(lyx_text):
            if (lyx_text[n].startswith('name "text:')):
                tag = lyx_text[n].replace('name "text:','',1).rstrip('"\n').lower()
                if tag in text.results:
                    # Insert text after preceding layout is closed
                    insert_now = False
                    i = n
                    while insert_now is False:
                        i+=1
                        if lyx_text[i]=='\\end_layout\n':
                            insert_now = True
                    
                    # Insert text
                    for key in text.results:
                        if tag==key:
                            lyx_code = write_data_to_lyx(text.results[key], args['size'])
                    lyx_text.insert(i+1, lyx_code)
        else:
            loop = False
    
    outfile = open(args['output'], 'wb')
    outfile.write( ''.join(lyx_text) )
    outfile.close()
    
    return lyx_text

def write_data_to_lyx(data, size):
    data_list = data.split('\n')
    linewrap_beg = '\\begin_layout Plain Layout\n'
    linewrap_end = '\\end_layout\n'
    if size!='Default':
        size_line = '\\backslash\n' + size + '\n' + linewrap_end + linewrap_beg
    else:
        size_line = ''
    
    preamble = '\\begin_layout Plain Layout\n' \
               '\\begin_inset ERT status collapsed\n' \
               '\\begin_layout Plain Layout\n' + size_line + \
               '\\backslash\nbegin{verbatim}\n' \
               '\end_layout'
    postamble = '\\begin_layout Plain Layout\n' \
                '\\backslash\nend{verbatim}\n' \
                '\end_layout\n' \
                '\end_inset\n' \
                '\end_layout'
    
    lyx_code = preamble
    for line in data_list:
        lyx_code += linewrap_beg + line + linewrap_end
    lyx_code += postamble
    
    return lyx_code
