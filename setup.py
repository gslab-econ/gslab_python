import os
import re
import sys
import shutil
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from glob import glob
 
# Determine if the user has specified which paths to report coverage for
is_include_arg = map(lambda x: bool(re.search('^--include=', x)), 
                     sys.argv)

if True in is_include_arg:
    include_arg = sys.argv[is_include_arg.index(True)]
    include_arg = sys.argv[is_include_arg.index(True)]
    del sys.argv[is_include_arg.index(True)]
else:
    include_arg = None


class TestRepo(build_py):
    '''Build command for running tests in repo'''
    def run(self):
        if include_arg:
            coverage_command = 'coverage report -m %s' % include_arg
        else:
            coverage_command = 'coverage report -m --omit=setup.py,*/__init__.py'


        if sys.platform != 'win32':
            os.system("coverage run --branch --source ./ setup.py test1 2>&1 "
                      "| tee test.log")
            # http://unix.stackexchange.com/questions/80707/
            #   how-to-output-text-to-both-screen-and-file-inside-a-shell-script
            os.system("%s  2>&1 | tee -a test.log" % coverage_command) 
        else:
            os.system("coverage run --branch --source ./ setup.py "
                      "> test.log")
            os.system("%s >> test.log" % coverage_command)

        sys.exit()


class CleanRepo(build_py):
    '''Build command for clearing setup directories after installation'''
    def run(self):
        # i) Remove the .egg-info folder
        egg_directories = glob('./*.egg-info')
        map(shutil.rmtree, egg_directories)
        # ii) Remove the ./build and ./dist directories
        if os.path.isdir('./build'):
            shutil.rmtree('./build')
        if os.path.isdir('./dist'):
            shutil.rmtree('./dist')

# Requirements
requirements = ['requests']

setup(name         = 'GSLab_Tools',
      version      = '3.0.4',
      description  = 'Python tools for GSLab',
      url          = 'https://github.com/gslab-econ/gslab_python',
      author       = 'Matthew Gentzkow, Jesse Shapiro',
      author_email = 'gentzkow@stanford.edu, jesse_shapiro_1@brown.edu',
      license      = 'MIT',
      packages     = find_packages(),
      install_requires = requirements,
      zip_safe     = False,
      cmdclass     = {'test': TestRepo, 'clean': CleanRepo},
      setup_requires = ['pytest-runner', 'coverage'],
      tests_require = ['pytest', 'coverage'])

