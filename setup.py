import os
import sys
import shutil
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from glob import glob
 
if sys.argv[-1] == 'test': # https://www.pydanny.com/python-dot-py-tricks.html
  os.system("python setup.py install clean")
  os.system("coverage run --branch --source ./ setup.py test1 > test.log")
  os.system("coverage report -m >> test.log")
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
      version      = '3.0.0',
      description  = 'Python tools for GSLab',
      url          = 'https://github.com/gslab-econ/gslab_python',
      author       = 'Matthew Gentzkow, Jesse Shapiro',
      author_email = 'gentzkow@stanford.edu, jesse_shapiro_1@brown.edu',
      license      = 'MIT',
      packages     = find_packages(),
      zip_safe     = False,
      cmdclass     = {'clean': CleanRepo},
      setup_requires = ['pytest-runner', 'coverage'],
      tests_require = ['pytest', 'coverage'])
