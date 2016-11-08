#! /usr/bin/env python

import subprocess
import os
import sys
import datetime
import time
import locale

#****************************************************
# MAKE.PY STARTS
#****************************************************

def main():
    start_make_log('./log/make.log', './log/')
    run_tests('./log/make.log', './log/test.log')
    end_make_log('./log/make.log')


def start_make_log(makelog, output_dir):
    
    print "\nStart log file: ", makelog
    
    if not os.path.isdir(output_dir):        
        os.makedirs(output_dir)

    LOGFILE = open(makelog, 'wb')    
    
    time_begin  = datetime.datetime.now().replace(microsecond = 0)
    sys.stderr  = LOGFILE
    working_dir = os.getcwd()
    
    print >> LOGFILE, '\n make.py started:', time_begin, working_dir, '\n\n'    
    
    # LIST FILES IN ./log DIRECTORY
    print >> LOGFILE, '\n'
    print >> LOGFILE, 'List of all files in sub-directories in', output_dir
    
    created   = os.stat(output_dir).st_mtime                
    asciiTime = time.asctime(time.localtime(created))     
    
    print >> LOGFILE, output_dir
    print >> LOGFILE, 'created/modified', asciiTime
    
    files = os.listdir(output_dir)
    
    for name in files:
        if not name.startswith('.'):
            full_name = os.path.join(output_dir, name)
            created   = os.path.getmtime(full_name)
            size      = os.path.getsize(full_name)
            asciiTime = time.asctime(time.localtime(created))
            
            print >> LOGFILE, '%50s' % name, '--- created/modified', asciiTime, \
                '(', locale.format('%d', size, 1), 'bytes )'
            
            if name != 'make.log':
                os.remove(os.path.join(output_dir, name))
    
    LOGFILE.close()             


def run_tests(makelog, test_log):    
    # RUN ALL TESTS
    command = 'python run_all_tests.py'
    LOGFILE = open(makelog, 'ab')
    
    TESTLOG = open(test_log, 'wb')
    print 'Executing: ', command
    subprocess.check_call(command, shell = True, stdout = TESTLOG, stderr = TESTLOG)
    TESTLOG.close()
    
    LOGFILE.write(open(test_log, 'rU').read())
    LOGFILE.close()     


def end_make_log(makelog):    
    # END MAKE LOG
    print "\nEnd log file: ", makelog
    LOGFILE = open(makelog, 'ab')
    time_end = datetime.datetime.now().replace(microsecond = 0)
    print >> LOGFILE, '\n make.py ended:', time_end
    LOGFILE.close()


main()

raw_input('\n Press <Enter> to exit.')