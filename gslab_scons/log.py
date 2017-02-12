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

    # scan sconstruct.log for start time
    # this looks unpythonic, but see xkcd 1171
    # probably should abstract this part out to helper
    with open('sconstruct.log', "r") as f:
        s = f.readline()
        s = s[s.find('{')+1: s.find('}')]
        start_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    # gather all sconscript logs (snippet from SO 3964681)
    # abstract this eyesore out to helper function...
    builder_log_collect = {}
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith("sconscript.log"):
                full_file = os.path.join(root, file)
                with open(full_file, 'rU') as f:
                    s = f.readlines()[1]
                    s = s[s.find('{')+1: s.find('}')]
                    builder_log_end_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                builder_log_collect[full_file] = builder_log_end_time
    this_run_file_dict = {key:value for key, value in builder_log_collect.items() if value > start_time}
    this_run_file_list = sorted(this_run_file_dict, key=this_run_file_dict.get, reverse=True)

    with open('sconstruct.log', "a") as sconstruct:
        for file in this_run_file_list:
            with open(file, 'rU') as sconscript:
                sconstruct.write(sconscript.read())
                sconstruct.write(end_of_file())

    return None

def log_timestamp(start_time, end_time, filename = 'sconstruct.log'):
    '''Adds beginning and ending times to a log file.'''
    with open(filename, mode = 'r+U') as f:
        content = f.read()
        f.seek(0, 0)
        builder_log_msg = '*** Builder log created: {%s} \n' + '*** Builder log completed: {%s} \n %s'
        f.write(builder_log_msg % (start_time, end_time, content))
    return None

