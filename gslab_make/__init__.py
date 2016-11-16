#!/usr/bin/python
# -*- coding: latin-1 -*-
'''
======================================
gslab_make: a library of make.py tools
======================================

Description:
make.py is a Python script that facilitates running programs in batch mode. 
It uses functions in this directory to provide efficient and easy-to-understand 
commands, which are portable across different Unix/Windows systems.

Prerequisites:
*  Python 2.7 installed and executable path is added to system path
*  SVN Version 1.7 or higher. See ‘clear_dirs’ command.

To use those commands in this library that call software other than Python or SVN, 
you must have this software installed with its executable path added to the
system path or defined as an environment variable/symbolic link. 
This remark applies to: Matlab, Stata, Perl, Mathematica 8.0 (the math kernel path
must be added to system path), StatTransfer, LyX, R, and SAS.

Notes:
*  In the statements of function syntax in this library, optional parameters are in [].
*  Default parameters, options, and executables used in make.py scripts are defined in
   /private/metadata.py. The file extensions associated with various software packages are
   also defined in this file. 
*  See run_program.py's docstring for information on its functions' required and optional
   keyword arguments.

====================================================
Information for make_links.py and make_link_logs.py
====================================================

Description:
`make_links()` and `make_link_logs()` parse and interpret
links files and use their contents to create, respectively,
symlinks and logs containing descriptive information. 
See the `make_links()` and `make_link_logs()` docstrings. for
more information on their functionalities. 

Usage:
See the `make_links()` and `make_link_logs()` docstrings. 

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


from get_externals import get_externals
from get_externals_github import get_externals_github

from make_log import set_option, start_make_logging, end_make_logging

from dir_mod import clear_dirs

from run_program import run_stata, run_matlab, run_perl, run_python, run_mathematica
from run_program import run_stc, run_stcmd, run_lyx, run_rbatch
from run_program import run_rinstall, run_sas, run_command
