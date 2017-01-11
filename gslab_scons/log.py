import os
import sys
import shutil
import subprocess
import misc
from datetime import datetime


def start_log(log = 'sconstruct.log'):
    '''Begins logging a build process'''
    misc.check_lfs()

    if misc.is_unix():
        sys.stdout = os.popen('tee %s' % log, 'wb')
    elif sys.platform == 'win32':
        sys.stdout = open(log, 'wb')

    sys.stderr = sys.stdout 
    return None


def log_timestamp(start_time, end_time, filename):
    '''Adds beginning and ending times to a log file.'''
    with open(filename, mode = 'r+U') as f:
        content = f.read()
        f.seek(0, 0)
        f.write('Log created:    ' + start_time + '\n' + 
                'Log completed:  ' + end_time   + '\n \n' + content)
    return None
