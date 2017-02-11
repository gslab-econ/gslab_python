import os
import sys
import gslab_scons.misc as misc

def start_log(mode, vers, log = 'sconstruct.log'):
    '''Begins logging a build process'''
    misc.check_lfs()
    
    if not (mode in ['develop', 'cache', 'release']):
        raise Exception("Error: %s is not a defined mode" % mode)
    if mode == 'release' and vers == '':
        raise Exception("Error: Version must be defined in release mode")

    start_message = "\n{0}{0}{0} New build: %s {0}{0}{0}" % misc.current_time()
    with open(log, "a") as f:
        f.write(start_message.format("*"))

    if misc.is_unix():
        sys.stdout = os.popen('tee -a %s' % log, 'wb')
    elif sys.platform == 'win32':
        sys.stdout = open(log, 'ab')
    sys.stderr = sys.stdout 
    print start_message.format("^")

    return None


def log_timestamp(start_time, end_time, filename = 'sconstruct.log'):
    '''Adds beginning and ending times to a log file.'''
    with open(filename, mode = 'r+U') as f:
        content = f.read()
        f.seek(0, 0)
        f.write('''
                *** Builder log created: %s 
                *** Builder log completed: %s
                %s
                ''' % (start_time, end_time, content))
    return None
