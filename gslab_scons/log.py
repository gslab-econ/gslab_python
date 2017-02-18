import os
import sys
import glob
from datetime import datetime
import gslab_scons.misc as misc

def start_log(mode, vers, log = 'sconstruct.log'):
    '''Begins logging a build process'''
    misc.check_lfs()
    
    if not (mode in ['develop', 'cache', 'release']):
        raise Exception("Error: %s is not a defined mode" % mode)
    if mode == 'release' and vers == '':
        raise Exception("Error: Version must be defined in release mode")

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

    end_message = "*** Build completed: {%s} ***\n" % misc.current_time()
    with open(log, "a") as f:
        f.write(end_message)

    # scan sconstruct.log for start time (if looks unpythonic, see xkcd 1171)
    with open('sconstruct.log', "rU") as f:
        s = f.readline()
        s = s[s.find('{')+1: s.find('}')]
        start_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    # gather all sconscript logs 
    parent_dir = os.getcwd()
    builder_logs = collect_builder_logs(parent_dir)
    
    # keep only builder logs from this run
    this_run_dict = {key:value for key, value in builder_logs.items() if value > start_time}
    this_run_list = sorted(this_run_dict, key=this_run_dict.get, reverse=True)

    with open('sconstruct.log', "a") as sconstruct:
        for f in this_run_list:
            with open(f, 'rU') as sconscript:
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
    ''' Recursively return dictionary of files ending with sconscript.log 
        in parent_dir and nested directories.
        Also return timestamp from those sconscript.log 
        (snippet from SO 3964681)'''
    builder_log_collect = {}

    for root, dirs, files in os.walk(parent_dir): # take a walk in parent and child dirs
        for f in files:
            if f.endswith("sconscript.log"):
                f_full = os.path.join(root, f)
                with open(f_full, 'rU') as f:
                    s = f.readlines()[1] # skip a line
                    s = s[s.find('{')+1: s.find('}')] # find {} time identifier 
                    builder_log_end_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                builder_log_collect[f_full] = builder_log_end_time

    return builder_log_collect
