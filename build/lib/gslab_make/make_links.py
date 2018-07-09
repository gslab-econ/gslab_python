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
    '''Import the make_links function from the make_links.py module.

    Description:
    This function parses and interprets links files and uses that input to create symlinks
    to large data files (symlinks allow shortcuts to be made locally so that programs will
    act as if the files are stored locally, but no local hard drive space is taken up)

    Syntax:
    make_links(links_files [, links_dir [, makelog  [, quiet]]])
     
    Parameters:
    - links_files: A string containing the name of a valid links file, a string containing
      multiple names of valid links files (delimited by spaces), or a Python list of
      strings in which each element is a valid links file. Each string may also contain one
      wildcard (as an asterisk). For example:
        `make_links('./links.txt')`, or
        `make_links('../external/links1.txt ../external/links2.txt')`, or
        `make_links(['../external/links1.txt', '../external/links2.txt'])`, or
        `make_links('../external/links*.txt')`.
        
        To get every file in a directory, simply end the string with a wild card:

            `make_links('../external/links_files/*')`
    
        There is no default argument for this parameter; links_files must be included in
        every call to make_links().
    
    - links_dir: A string containing the name of the local directory into which the symlinks 
        will be created. The default argument for this parameter is '../external_links/'.
    
    - makelog: A string containing the name of the makelog that will store make_links()
        output. If makelog is an empty string (i.e. ''), the default log file will be
        unchanged. The default argument for this parameter is '../output/make.log'.
    
    - quiet: A boolean. Setting this argument to True suppresses standard output and errors
        from svn. The default argument for this parameter is False.
    
    Caution:
    
    Take care when dealing with symlinks. Most programs will treat the links as if they are
    the file being linked to. For instance, if ../data_links/some_data.dta is a link to 
    \external_source\some_data.dta and Stata opens ../data_links/some_data.dta, edits it,
    and saves it to the same location, the original file (\external_source\some_data.dta)
    will be changed. In such a case, it would probably be preferable to save a local copy of
    the data and make changes to that file.   
    '''
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
