from setuptools import setup, find_packages

setup(name='gslab',
      version='1.0',
      description='python package for GSLab',
      url='git@github.com:gslab-econ/GSLab.git',
      author='GSLab',
      author_email='GSLab@stanford.edu',
      license='MIT',
      packages = find_packages(),
      zip_safe=False)