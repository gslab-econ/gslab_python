#! /usr/bin/env python
#****************************************************
# GET LIBRARY
#****************************************************
import os
#gslab_make_path = os.getenv('gslab_make_path')
#subprocess.call('svn export --force -r 33474 ' + gslab_make_path + ' gslab_make', shell = True)
from gslab_make.py.get_externals import *
from gslab_make.py.get_externals_github import *
from gslab_make.py.make_log import *
from gslab_make.py.run_program import *
from gslab_make.py.dir_mod import *

#****************************************************
# MAKE.PY STARTS
#****************************************************

# SET DEFAULT OPTIONS
set_option(makelog = 'log/make.log', output_dir = './log', temp_dir = './temp')
clear_dirs('./external/','./temp')
delete_files('./log/*')
start_make_logging()

# GET EXTERNALS
get_externals('externals.txt', './external/')

# RUN ALL TESTS
run_stata(program = 'test/setup.do', log = 'log/test.log', changedir = True)
run_python(program = 'test/run_all_tests.py', log = 'log/test.log', changedir = True)

end_make_logging()

shutil.rmtree('gslab_make')
raw_input('\n Press <Enter> to exit.')
