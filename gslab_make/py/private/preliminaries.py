#! /usr/bin/env python

import sys
import os
import datetime
import re
import traceback
import shutil

import messages as messages
import metadata as metadata
from exceptionclasses import CustomError, CritError
from getexternalsdirectives import SystemDirective, SvnExportDirective, CopyDirective, GitHubDirective


######################################################
# Logging
######################################################

def start_logging(log, logtype):
    try:
        LOGFILE = open(log,'wb') 
    except:
        raise CustomError.crit(messages.crit_error_log % log)
    time_begin = datetime.datetime.now().replace(microsecond=0)
    orig_stderr = sys.stderr
    sys.stderr = LOGFILE
    working_dir = os.getcwd()
    print >> LOGFILE, messages.note_logstart % logtype, time_begin, working_dir

    return LOGFILE

def end_logging(LOGFILE, makelog, logtype):
    time_end = datetime.datetime.now().replace(microsecond=0)
    print >> LOGFILE, messages.note_logend % logtype,time_end
    LOGFILE.close()
    if not makelog: return
    if not (metadata.makelog_started and os.path.isfile(makelog)):
        raise CritError(messages.crit_error_nomakelog % makelog)
    MAKE_LOGFILE = open(makelog, 'ab')
    MAKE_LOGFILE.write( open(LOGFILE.name, 'rU').read() )
    MAKE_LOGFILE.close()
    os.remove(LOGFILE.name)


######################################################
# Input_to_array
######################################################

def input_to_array(filename):
    # Import file
    try:
        FILENAME = open(filename, 'rU')
    except:
        raise CritError(messages.crit_error_file % filename)

    # Delete header
    filearray = []
    for line in FILENAME:
        if ( not re.match('rev', line) and not re.match('linkpath', line)
             and not re.match('\s*\#',line) and not re.match('\s*$',line) and not re.match('url', line)):
            filearray.append(line.rstrip('\n'))
    FILENAME.close()

    return filearray
    
######################################################
# Print Error
######################################################

def print_error(LOGFILE):
    print '\n'
    print >> LOGFILE, '\n'
    print 'Error Found'
    traceback.print_exc(file = LOGFILE)        
    traceback.print_exc(file = sys.stdout)
    
def add_error_to_log(makelog):
    if not makelog: return
    if not (metadata.makelog_started and os.path.isfile(makelog)):
        raise CritError(messages.crit_error_nomakelog % makelog)
    LOGFILE = open(makelog, 'ab')
    print_error(LOGFILE)
    LOGFILE.close()
   
######################################################
# Walk through directories
######################################################
def files_list (read_dir, recur_lim):
    """Generate a list of all files in "read_dir" and its subdirectories (up to
    a depth of "recur_lim" -- if recur_lim is 0, there is no depth limit)."""
    
    all_files = []
    
    walk = walk_dir(read_dir, recur_lim)
    
    for dir_name, file_list in walk:
        for file_name in file_list:
            all_files.append(os.path.join(dir_name, file_name))

    all_files.sort()
    return all_files  
    
def walk_dir(read_dir, recur_lim):
    """ Yields a matching of all non-hidden subdirectories of "read_dir" to the
    files in the subdirectories up to a depth of "recur_lim" -- if recur_lim is 
    0 (or False), there is no depth limit. """ 
    
    if in_current_drive(read_dir):
        read_dir = os.path.abspath(read_dir)
        
    if recur_lim:
        dir_files = walk_lim(read_dir, 1, recur_lim)
        for i in range(len(dir_files)):
            yield dir_files[i]
    else:
        for root, dirs, files in os.walk(read_dir):
            if in_current_drive(root):
                root = os.path.abspath(root)
            this_dir = os.path.basename(root)
            if not this_dir.startswith('.'):
                files = [ f for f in files if not f.startswith('.') ]
                yield root, files
            else:
                del dirs[:]
                
def walk_lim (read_dir, current_depth, recur_lim):
    """Recursively match all non-hidden files and subdirectories of "read_dir",
    where read_dir is "current_depth" directories deep from the original 
    directory, and there is a maximum depth of "recur_lim" """
    
    if in_current_drive(read_dir):
        read_dir = os.path.abspath(read_dir)
    dir_list = os.listdir(read_dir)
    
    files = [ f for f in dir_list if os.path.isfile(os.path.join(read_dir, f)) ]
    files = [ f for f in files if not f.startswith('.') ]

    output = [[read_dir, files]]
    
    current_depth = current_depth + 1
    
    if current_depth <= recur_lim:
        dirs = [ d for d in dir_list if os.path.isdir(os.path.join(read_dir, d)) ]
        dirs = [ d for d in dirs if not d.startswith('.') ]
        for d in dirs:
            walk = walk_lim(os.path.join(read_dir, d), 
                            current_depth,
                            recur_lim)
            for w in walk:
                output.append(w)

    return output    
    
def in_current_drive (dir):
    current_drive = os.path.splitdrive(os.getcwd())[0]
    other_drive = os.path.splitdrive(dir)[0]
    return current_drive == other_drive
 

######################################################
# get_externas[_github] preliminaries
###################################################### 
    
def externals_preliminaries(makelog, externals_file, LOGFILE):
    if makelog == '@DEFAULTVALUE@':
        makelog = metadata.settings['makelog_file']
    if externals_file!='externals.txt':
        print >> LOGFILE, messages.note_extfilename        
    externals = input_to_array(externals_file)

    # Prepare last rev/dir variables
    last_dir = ''
    last_rev = ''    
    return([makelog, externals, last_dir, last_rev])
        
