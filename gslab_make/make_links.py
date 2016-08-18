'''
=================================================
Readme for make_links.py and make_link_logs.py
==================================================


Description:
make_links.py - parses and interprets links files and uses that input to create symlinks
to large data files (symlinks allow shortcuts to be made locally so that programs will
act as if the files are stored locally, but no local hard drive space is taken up)

make_link_logs.py - parses and interprets links files and uses that input to create logs
of useful information regarding where local shortcuts point to and information regarding
when and how the linked files were last changed

Usage:

---------------
make_links.py:
---------------

Import the make_links function from the make_links.py module.

```
make_links (links_files 
        [, links_dir 
        [, makelog 
        [, quiet]]])
```        

- links_files: A string containing the name of a valid links file, a string containing
  multiple names of valid links files (delimited by spaces), or a Python list of
  strings in which each element is a valid links file. Each string may also contain one
  wildcard (as an asterisk). For example:

        `make_links('./links.txt')`

    Or:
    
        `make_links('../external/links1.txt ../external/links2.txt')`
    
    Or:

       `make_links(['../external/links1.txt', '../external/links2.txt'])`
    
    Or:
    
        `make_links('../external/links*.txt')`
    
    To get every file in a directory, simply end the string with a wild card:
    
        `make_links('../external/links_files/*')`

    There is no default argument for this parameter; links_files must be included in
    every call to make_links().

- links_dir: A string containing the name of the local directory into which the symlinks 
    will be created.

  -  The default argument for this parameter is '../external_links/'.

- makelog: A string containing the name of the makelog that will store make_links()
    output. If makelog is an empty string (i.e. ''), the default log file will be
    unchanged.

  -  The default argument for this parameter is '../output/make.log'.

- quiet: A boolean. Setting this argument to True suppresses standard output and errors
    from svn.

  -  The default argument for this parameter is False.

Caution:

Take care when dealing with symlinks. Most programs will treat the links as if they are
the file being linked to. For instance, if ../data_links/some_data.dta is a link to 
\external_source\some_data.dta and Stata opens ../data_links/some_data.dta, edits it,
and saves it to the same location, the original file (\external_source\some_data.dta)
will be changed. In such a case, it would probably be preferable to save a local copy of
the data and make changes to that file.   

-------------------
make_link_logs.py:
-------------------

Import the make_link_logs function from the make_link_logs.py module.

```
def make_link_logs (links_files
                    [, links_dir
                    [, link_logs_dir
                    [, link_stats_file
                    [, link_heads_file
                    [, link_orig_file
                    [, recur_lim]]]]]])
```                    

- links_files: See the description in make_links.py above.

- links_dir: See the description in make_links.py above.

- link_logs_dir: A string containing the name of the directory into which the log files will
    be saved.

  -  The default argument for this parameter is '../log/'.

- link_stats_file: A string containing the name of the link stats file (see below for 
    full explanation of what this file contains). To prevent this log from being 
    made, set this argument to an empty string (i.e. ''). This is the name of the 
    file only; the directory name is determined by link_logs_dir.

  -  The default argument for this parameter is 'link_stats.log'.

- link_head_file: Same as link_stats_file above except for the link heads file.

  -  The default argument for this parameter is 'link_heads.log'.

- link_orig_file: Same as link_stats_file above except for link origins file.

  -  The default argument for this parameter is 'link_orig.log'

- recur_lim: An integer which determines the directory depth to which the log files will
    search for a list in the links_dir. By default, this argument is 2, which searches 
    links_dir and one level of subdirectories. If the argument is changed to 1, the log 
    files would only search in links_dir, and if it was changed to 3 the log files would 
    search in links_dir and 2 levels of subdirectories (and so on). If the argument is 
    set to 0, there is no depth limit.

  -  The default argument for this parameter is 2.


Description of log files:
    - link_stats_file: stores all file names, date and time last modified, and file sizes

    - link_heads_file: stores the first ten lines of all readable files 

    - link_orig_file:  stores the local names of all symlinks and the original files to 
                       which they point; if a directory is a symlink, only the directory 
                       will be included in the mapping, even though it's contents will 
                       technically be links, too

------------------------------------------
Both make_links.py and make_link_logs.py:
------------------------------------------

Prequisites:
(1) Python 2.7 installed and defined as an environment variable.

As with get_externals.py, when make_links.py and make_link_logs.py are called, the .py
files in /private/ will be compiled into .pyc compiled files (which Python then reads).
 These are placed in the ./private/__pycache___ directory.

For both make_links and make_link_logs, the links_files option is required. The rest of
the arguments are optional. All optional arguments can be specified by key word 
arguments.

The links_dir argument should be the same for both make_links and make_link_logs (this is
true by default). If both make_links and make_link_logs are being called, the best way to
change links_dir is to change the 'links_dir' setting using set_option(). For example:

`set_option(links_dir = '../different_links_dir')`

When calling both make_links and make_link_logs, it is wise to define a links_list
variable and pass that as the argument to both make_links and make_link_logs. For
example:

```
links_list = ['../external/links1.txt', '../external/links2.txt']
make_links(links_list)
make_link_logs(links_list)
```

=======================
links.txt File Format:
=======================
This file needs to rows of numbers or characters, delimited by either tabs or 4 spaces.
The proper format is: 

`localname  linkpath`


Column descriptions:
---------------------

- localname:  
  -  The local name of the link. Relative paths will be made relative to the links_dir
            parameter (default parameter: "../data_links"). If linkpath is a file, and no file is
            given in localname, the local name of the link will be the name of the linked file.
            Directories must be explicitly named; that is, if linkpath is a directory, and no
            directory name is given in localname (i.e. localname is simply "./"), the contents of
            linkpath will be linked directly in links_dir. If, instead, you want to link to a
            directory called '/data_files/' and name the local directory 'data_files', the
            localname argument must be './data_files/'. Additionally, make_links has the 
            capability to assign a prefix tag to a collection of files to be linked, either through
            a folder link, or wildcard call. In order to do so, end the localname column with
            '[prefix]*', where the prefix [prefix] will be attached to each linked file. See below
            for an example of prefixing. If linkpath includes a wildcard, localname should either
            specify a directory into which all the files will go or include a wildcard (for
            instance, when adding prefixes).

  -  linkpath:   
    -  The file or directory to which the link will point. If linkpath is a directory, the
            entire directory will be linked. If linkpath is a file, only the file will be linked.
            If a file name wildcard is required, place  single * within filename (i.e., test*.txt 
            will call test1.txt, test2.txt, and any file of this form). make_links.py will also 
            attempt to screen out bad file names. Cannot be left blank.         
            

Example of links.txt:
----------------------

```
./Booth_ConsumerPanel_20121228/ //centers.chicagobooth.edu/nielsen_extracts/Homescan/Booth_ConsumerPanel_20121228/
./2010_data/    //centers.chicagobooth.edu/nielsen_extracts/Homescan/PrePilot_20121117/*_10.tsv
./rms_stores.tsv    //centers.chicagobooth.edu/nielsen_extracts/RMS/stores.tsv
```

Example of prefixing:
----------------------
Suppose a directory called ./test_dir/ which contains the following files:

```
    - ./test_dir/
        > one.txt
        > two.txt
        > output.dta
```        
        
Consider the following links.txt:

`./test_*    ./test_dir/`

make_links.py will prepend 'test_' to all the links that get created:

```
    - ./external_links/
        > test_one.txt
        > test_two.txt
        > test_output.dta
```        

Commenting in links.txt:
-------------------------
Although not entirely recommended (comments should be migrated to readme.txt), one can 
place comments in links.txt by leading off a line with a #. Note, however, that a # 
anywhere else in a line will not be read as a comment.

Error Logging:
---------------
The program is designed to catch as many errors as possible. The error_check() method 
checks key syntax requirements are satisfied. However, it doesn't check for all errrors.

Instead, if a line of links.txt is illegal, the error will be caught before or as the 
final command is issued. An example of the former case is trying to issue the command

```
    string = 'fig_*2*.txt'
    one,two = string.split('\*')
```    

i.e. trying to force three objects into two. The error message, and traceback to its' location, is 
then printed to the logfile. If a line fails at execution, the error is again printed to the logfile, 
as well as the raw input line from links.txt. Instead of make_links providing the user a 
detailed list of possible causes, the user should examine the raw input and correct so the desired
file is exported.
'''
#! /usr/bin/env python

import os

from dir_mod import remove_dir
from private.linkslist import LinksList
from private.preliminaries import start_logging, end_logging
import private.metadata as metadata

def make_links (links_files,
                links_dir = '@DEFAULTVALUE@',
                makelog = '@DEFAULTVALUE@',                    
                quiet = False):

    try:         
        if makelog == '@DEFAULTVALUE@':
            makelog = metadata.settings['makelog_file']
            
        # Run preliminaries
        LOGFILE = start_logging(metadata.settings['linkslog_file'], 'make_links.py')

        list = LinksList(links_files, links_dir)
        
        if os.path.exists(list.links_dir):
            remove_dir(list.links_dir)
        os.makedirs(list.links_dir)        
        
        list.issue_sys_command(LOGFILE, quiet)
                                  
        end_logging(LOGFILE, makelog, 'make_links.py')
    
    except Exception as errmsg:
        print "Error with make_links: \n", errmsg                      
