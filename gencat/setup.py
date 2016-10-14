from setuptools import setup, find_packages

setup(name             = 'GSLab_Gencat',
      version          = '0.0.2',
      description      = 'A class to unzip and concatenate, and rezip files.',
      url              = 'https://github.com/gslab-econ/gslab_python/tree/issue13-subgroupzip/gencat',
      author           = 'Matthew Gentzkow, Jesse Shapiro',
      author_email     = 'gentzkow@stanford.edu, jesse_shapiro_1@brown.edu',
      license          = 'MIT',
      packages         = find_packages(),
      zip_safe         = False,)
