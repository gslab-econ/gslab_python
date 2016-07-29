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
