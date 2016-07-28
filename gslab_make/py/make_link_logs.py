#! /usr/bin/env python

import os
import re
import datetime

from make_log import make_stats_log, make_heads_log
from private.linkslist import LinksList
import private.metadata as metadata

def make_link_logs (links_files,
                    links_dir = '@DEFAULTVALUE@',
                    link_logs_dir = '@DEFAULTVALUE@',
                    link_stats_file = '@DEFAULTVALUE@', 
                    link_heads_file = '@DEFAULTVALUE@',
                    link_orig_file = '@DEFAULTVALUE@',
                    recur_lim = 2):
    """Create three log files for the files in "read_dir" and its
    subdirectories (up to a depth of "recur_lim" -- if recur_lim is 0, there is
    no depth limit). The three files are a stats file, a headers file, and a
    symlink origins file. All three will append to existing results if the
    existing file has the correct header.""" 
    
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
    """Using the mappings from "links_dict", Create a log file at  
    "link_orig_file" in "link_logs_dir" of the local names of symlinks and the
    original files to which they link."""
    
    if link_orig_file == '':
        return
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
        
      
