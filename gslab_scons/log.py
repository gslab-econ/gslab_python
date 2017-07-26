import os
import sys
import glob
from datetime import datetime
import subprocess
import gslab_scons.misc as misc


def start_log(mode, vers, log = 'sconstruct.log'):
    '''Begins logging a build process'''
    
    if not (mode in ['develop', 'cache']):
        raise Exception("Error: %s is not a defined mode" % mode)

    start_message = "*** New build: {%s} ***\n" % misc.current_time()
    with open(log, "w") as f:
        f.write(start_message)

    if misc.is_unix():
        sys.stdout = os.popen('tee -a %s' % log, 'wb')
    elif sys.platform == 'win32':
        sys.stdout = open(log, 'ab')

    sys.stderr = sys.stdout 

    return None


def end_log(log = 'sconstruct.log'):
    '''Complete the log of a build process.'''

    end_message = "*** Build completed: {%s} ***\n \n \n" % misc.current_time()
    with open(log, "a") as f:
        f.write(end_message)

    # scan sconstruct.log for start time
    with open('sconstruct.log', "rU") as f:
        s = f.readline()
        s = s[s.find('{') + 1: s.find('}')]
        start_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    # gather all sconscript logs 
    parent_dir = os.getcwd()
    builder_logs = collect_builder_logs(parent_dir)
    
    # keep only builder logs from this run OR is broken (value == beginning_of_time)
    beginning_of_time    = datetime.min # to catch broken logs (see collect_builder_logs)
    this_run_dict = {key:value for key, value in builder_logs.items() if (value > start_time) or value == beginning_of_time}
    this_run_list = sorted(this_run_dict, key=this_run_dict.get, reverse=True)

    with open('sconstruct.log', "a") as sconstruct:
        for f in this_run_list:
            with open(f, 'rU') as sconscript:
                if this_run_dict[f] == beginning_of_time:
                    sconstruct.write("*** Warning!!! Doesn't look the sconscript below finished.\n")
                sconstruct.write(f)
                sconstruct.write(sconscript.read())

    return None


def log_timestamp(start_time, end_time, filename = 'sconstruct.log'):
    '''Adds beginning and ending times to a log file.'''
    with open(filename, mode = 'r+U') as f:
        content = f.read()
        f.seek(0, 0)
        builder_log_msg = '*** Builder log created: {%s} \n' + '*** Builder log completed: {%s} \n %s'
        f.write(builder_log_msg % (start_time, end_time, content))
    return None


def collect_builder_logs(parent_dir):
    ''' Recursively return dictionary of files named sconscript*.log 
        in parent_dir and nested directories.
        Also return timestamp from those sconscript.log 
        (snippet from SO 3964681)'''
    builder_log_collect = {}

    # Use platform-specific command line tool to search for paths tp logs 
    # and store them in a list
    log_name = 'sconscript*.log'
    sprintf_bundle = (parent_dir, log_name)
    if misc.is_unix():
        cmd = 'find %s -name "%s"' % sprintf_bundle
    else:
        cmd = 'dir %s %s /b/s' % sprintf_bundle
    log_paths = subprocess.check_output(cmd, shell = True)

    # Read the file at each path to a log and store output text in a dict at filename
    for log_path in log_paths:
        with open(log_path.strip(), 'rU') as f:
            try:
                s = f.readlines()[1] # line 0 = log start time, line 1 = log end time
            except IndexError:
                s = ''
            s = s[s.find('{')+1: s.find('}')] # find {} time identifier 
            try:
                builder_log_end_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except ValueError: # if the code breaks, there's no time identifier
                beginning_of_time    = datetime.min
                builder_log_end_time = beginning_of_time
        builder_log_collect[f_full]  = builder_log_end_time

    return builder_log_collect
