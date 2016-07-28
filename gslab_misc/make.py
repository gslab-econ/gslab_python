#! /usr/bin/env python
#****************************************************
# GET LIBRARY - Do not modify this section
#****************************************************
import subprocess, shutil
subprocess.check_call(r'svn export --force -r 16215 http://gsbhmg01.chicagobooth.edu/svn/trunk/lib/python/gslab_make/ gslab_make', shell = True)
from gslab_make.py.get_externals import *
from gslab_make.py.make_log import *
from gslab_make.py.run_program import *
from gslab_make.py.dir_mod import *

#****************************************************
# make.py starts: 
#****************************************************

# SET DEFAULT OPTIONS
set_option(makelog = './log/make.log', output_dir = './log', temp_dir = '', external_dir = './external')

start_make_logging()

# GET_EXTERNALS
get_externals('externals.txt')

# RUN TESTS
run_stata(program = './test/input/logs_for_textfill.do', changedir = True, log = './log/stata.log')
run_python(program = './test/run_all_tests.py', changedir = True, log = './log/test.log')

end_make_logging()

shutil.rmtree('gslab_make')
input('\n Press <Enter> to exit.')
