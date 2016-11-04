#! /usr/bin/env python
#****************************************************
# GET LIBRARY - Do not modify this section
#****************************************************
import os
import sys
sys.path.append('../../gslab_make') 
from get_externals import *
from make_log import *
from run_program import *
from dir_mod import *

#****************************************************
# make.py starts: 
#****************************************************

# SET DEFAULT OPTIONS
set_option(makelog = './log/make.log', output_dir = './log', temp_dir = '', external_dir = './external')

start_make_logging()

# RUN TESTS
run_python(program = './test/run_all_tests.py', changedir = True, log = './log/test.log')

end_make_logging()

input('\n Press <Enter> to exit.')
