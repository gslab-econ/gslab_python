#! /usr/bin/env python
#****************************************************
# GET LIBRARY
#****************************************************
import subprocess, shutil, os
from gslab_make.py.get_externals import *
from gslab_make.py.make_log import *
from gslab_make.py.run_program import *
from gslab_make.py.dir_mod import *

#****************************************************
# MAKE.PY STARTS
#****************************************************

# SET DEFAULT OPTIONS
set_option(makelog = 'log/make.log', output_dir = 'log', temp_dir = '')

start_make_logging()

# GET EXTERNALS
get_externals('externals.txt', './external')

# GET DEPENDS
get_externals('depends.txt', './depend')

# RUN ALL TESTS
run_python(program = './test/test_speech_from_phrase.py', changedir = True)

end_make_logging()

raw_input('\n Press <Enter> to exit.')
