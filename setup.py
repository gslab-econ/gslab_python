from setuptools import setup, find_packages

setup(name         = 'GSLab_Tools',
      version      = '1.1.1',
      description  = 'Python tools for GSLab',
      url          = 'https://github.com/gslab-econ/gslab_python',
      author       = 'Matthew Gentzkow, Jesse Shapiro',
      author_email = 'gentzkow@stanford.edu, jesse_shapiro_1@brown.edu',
      license      = 'MIT',
      packages     = find_packages(),
      zip_safe     = False,
      download_url = "https://github.com/gslab-econ/gslab_python/archive/v1.1.1.tar.gz")
