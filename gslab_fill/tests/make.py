#! /usr/bin/env python
#****************************************************
# GET LIBRARY - Do not modify this section
#****************************************************
import os
import sys
sys.path.append('../..') 
from gslab_make import (start_make_logging, end_make_logging, set_option,
                        get_externals, run_stata, run_python)

#****************************************************
# make.py starts: 
#****************************************************

# SET DEFAULT OPTIONS
set_option(makelog = './log/make.log', output_dir = './log', temp_dir = '', external_dir = './external')

start_make_logging()

# GET_EXTERNALS
get_externals('externals.txt')

# RUN TESTS
run_stata(program = './input/logs_for_textfill.do', changedir = True, log = './log/stata.log')
run_python(program = './run_all_tests.py', changedir = True, log = './log/test.log')

end_make_logging()
