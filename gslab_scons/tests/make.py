#! /usr/bin/env python

import os
import sys
sys.path.append('../../gslab_make') 
from make_log    import set_option, start_make_logging, end_make_logging
from run_program import run_python

# Set default options
set_option(makelog = './log/make.log', output_dir = './log', 
           temp_dir = '', external_dir = './external')

start_make_logging()

# Run tests
run_python(program = './run_all_tests.py', changedir = True, 
           log     = './log/test.log')

end_make_logging()
