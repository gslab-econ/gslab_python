import os, sys, shutil, subprocess
from datetime import datetime
from sys import platform
from misc import is_unix, check_lfs

def start_log(log = 'sconstruct.log'):
    check_lfs()
    if is_unix():
        sys.stdout = os.popen('tee %s' % log, 'w')
    elif platform == 'win32':
        sys.stdout = open(log, 'w')
    sys.stderr = sys.stdout 
    return None

def log_timestamp(start_time, end_time, filename):
    with open(filename, mode = 'r+U') as f:
        content = f.read()
        f.seek(0, 0)
        f.write('Log created:    ' + start_time + '\n' + 
                'Log completed:  ' + end_time   + '\n \n' + content)
    return None