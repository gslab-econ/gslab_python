import os
import shutil
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from glob import glob


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


setup(name         = 'GSLab_Tools',
      version      = '2.0.2',
      description  = 'Python tools for GSLab',
      url          = 'https://github.com/gslab-econ/gslab_python',
      author       = 'Matthew Gentzkow, Jesse Shapiro',
      author_email = 'gentzkow@stanford.edu, jesse_shapiro_1@brown.edu',
      license      = 'MIT',
      packages     = find_packages(),
      zip_safe     = False,
      cmdclass     = {'clean': CleanRepo})

