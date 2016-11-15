#! /usr/bin/env python

import os
import re
import datetime
import private.metadata as metadata

from make_log import make_stats_log, make_heads_log
from private.linkslist import LinksList


def make_link_logs (links_files,
                    links_dir = '@DEFAULTVALUE@',
                    link_logs_dir = '@DEFAULTVALUE@',
                    link_stats_file = '@DEFAULTVALUE@', 
                    link_heads_file = '@DEFAULTVALUE@',
                    link_orig_file = '@DEFAULTVALUE@',
                    recur_lim = 2):
    '''Import the make_link_logs function from the make_link_logs.py module.
   
    Description: 
    This function parses and interprets links files and uses that input to create logs
    of useful information regarding where local shortcuts point to and information regarding
    when and how the linked files were last changed

    Syntax:
    make_link_logs(links_files [, links_dir [, link_logs_dir [, link_stats_file
                   [, link_heads_file [, link_orig_file [, recur_lim]]]]]])
                      
    Parameters:
    - links_files: See `make_links`'s docstring.
    - links_dir: See `make_links`'s docstring.
    - link_logs_dir: A string containing the name of the directory into which the log files will
        be saved. The default argument for this parameter is '../log/'.
    - link_stats_file: A string containing the name of the link stats file (see below for 
        full explanation of what this file contains). To prevent this log from being 
        made, set this argument to an empty string (i.e. ''). This is the name of the 
        file only; the directory name is determined by link_logs_dir.
        The default argument for this parameter is 'link_stats.log'.
    - link_head_file: Same as link_stats_file above except for the link heads file.
        The default argument for this parameter is 'link_heads.log'.
    - link_orig_file: Same as link_stats_file above except for link origins file.
        The default argument for this parameter is 'link_orig.log'
    - recur_lim: An integer which determines the directory depth to which the log files will
        search for a list in the links_dir. By default, this argument is 2, which searches 
        links_dir and one level of subdirectories. If the argument is changed to 1, the log 
        files would only search in links_dir, and if it was changed to 3 the log files would 
        search in links_dir and 2 levels of subdirectories (and so on). If the argument is 
        set to 0, there is no depth limit. The default argument for this parameter is 2.
    
    
    Description of log files:
        - link_stats_file: stores all file names, date and time last modified, and file sizes
        - link_heads_file: stores the first ten lines of all readable files 
        - link_orig_file:  stores the local names of all symlinks and the original files to 
                           which they point; if a directory is a symlink, only the directory 
                           will be included in the mapping, even though it's contents will 
                           technically be links, too
    '''
    
    if link_logs_dir == '@DEFAULTVALUE@':
        link_logs_dir = metadata.settings['link_logs_dir']
    if link_stats_file == '@DEFAULTVALUE@':
        link_stats_file = metadata.settings['link_stats_file']
    if link_heads_file == '@DEFAULTVALUE@':
        link_heads_file = metadata.settings['link_heads_file']
    if link_orig_file == '@DEFAULTVALUE@':
        link_orig_file = metadata.settings['link_orig_file']
    
    links_list = LinksList(links_files, links_dir)
    sorted_files, links_dict = links_list.link_files_and_dict(recur_lim)          
    
    make_stats_log(link_logs_dir, link_stats_file, sorted_files)
    make_heads_log(link_logs_dir, link_heads_file, sorted_files)    
    make_link_orig_log(link_logs_dir, link_orig_file, links_dict)
    

def make_link_orig_log (link_logs_dir, link_orig_file, links_dict):
    """
    Using the mappings from the `links_dict` argument, create a log file at  
    `link_orig_file` in `link_logs_dir` that reports the local names
    of symlinks and the original files to which they link.
    """
    
    # Return if no link_orig_file is specified
    if link_orig_file == '':
        return
    
    # Return if the links_dict is empty
    num_links = len(links_dict.keys())
    if num_links == 0:
        return
        
    link_orig_path = os.path.join(link_logs_dir, link_orig_file)
    link_orig_path = re.sub('\\\\', '/', link_orig_path)
        
    header = "local\tlinked"

    if not os.path.isdir(os.path.dirname(link_orig_path)):
        os.makedirs(os.path.dirname(link_orig_path))
    ORIGFILE = open(link_orig_path, 'w+')
    print >> ORIGFILE, header  

    links_dict_it = iter(sorted(links_dict.iteritems()))
    for i in range(num_links):
        print >> ORIGFILE, "%s\t%s" % links_dict_it.next()
        
      
