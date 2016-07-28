#! /usr/bin/env python

import os
import re

from linkdirectives import *
from preliminaries import *
import metadata as metadata

class LinksList(object):

    def __init__ (self, file_list, links_dir = '@DEFAULTVALUE@'):
        if links_dir == '@DEFAULTVALUE@':
            links_dir = metadata.settings['links_dir']
        if links_dir[-1] != '/':
            links_dir = links_dir + '/'
        self.links_dir = links_dir
                    
        if type(file_list) is str:
            file_list = file_list.split(' ')
            
        self.links_files = []
        for f1 in file_list:
            if re.search('\*.+', f1) or re.search('^.+\*', f1) or re.search('\*', f1):
                # Make wildcard list
                wildfirst,wildlast = f1.split('*')
                file_dir,wildfirst = os.path.split(wildfirst)
                file_dir = os.path.abspath(file_dir)
                files = [ f2 for f2 in os.listdir(file_dir) 
                            if os.path.isfile(os.path.join(file_dir, f2)) ]
                for f3 in files:
                    if re.match('%s.*%s$' % (wildfirst,wildlast), f3):
                        self.links_files.append(os.path.join(file_dir, f3))
            else:
                self.links_files.append(f1)
                
        self.linkdirectives_list = []
        for f in self.links_files:
            lines = input_to_array(f)
            for line in lines:
                directive = LinkDirectives(line, self.links_dir)
                self.linkdirectives_list.append(directive)
                
    def issue_sys_command (self, logfile, quiet):        
        for link in self.linkdirectives_list:
            try:
                link.issue_sys_command(logfile, quiet)
            except:
                print_error(logfile)
    
    def link_files_and_dict (self, recur_lim):
        links_dict = {}
        for link in self.linkdirectives_list:
            links_dict = link.add_to_dict(links_dict)
        
        links = links_dict.values()
        sorted_files = [ f for f in links if os.path.isfile(f) ]
        if recur_lim > 1:
            dirs = [ d for d in links if os.path.isdir(d) ]
            for d in dirs:
                new_files = files_list(d, recur_lim - 1)
                sorted_files = sorted_files + new_files
        elif not recur_lim:
            dirs = [ d for d in links if os.path.isdir(d) ]
            for d in dirs:
                new_files = files_list(d, recur_lim)
                sorted_files = sorted_files + new_files
        sorted_files.sort()
            
        return sorted_files, links_dict
            

      
    

