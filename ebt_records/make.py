#! /usr/bin/env python
#****************************************************
# GET LIBRARY
#****************************************************
import os
from gslab_make.py.get_externals import *
from gslab_make.py.make_log import *
from gslab_make.py.run_program import *
from gslab_make.py.dir_mod import *
from gslab_make.py.make_links import *
from gslab_make.py.make_link_logs import *

#****************************************************
# MAKE.PY STARTS
#****************************************************

# SET DEFAULT OPTIONS
set_option(makelog = 'log/make.log', output_dir = './log')

clear_dirs('./log')
start_make_logging()

get_externals('externals.txt', './external')
make_links('./external/ebt_records_links.txt', './external_links')
make_link_logs('./external/ebt_records_links.txt', link_heads_file = "", link_stats_file = "")

# RUN ALL TESTS
run_python(program = 'test/run_all_tests.py', log = 'log/test.log', changedir = True)

end_make_logging()

raw_input('\n Press <Enter> to exit.')
