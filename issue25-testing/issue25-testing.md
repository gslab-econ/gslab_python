Notes on popular packages' testing frameworks
---------------------------------------------

### [SciPy](https://github.com/numpy/numpy/blob/master/doc/TESTS.rst.txt)
- SciPy has a `test()` function that runs all of its tests. These tests use [Nose](http://nose.readthedocs.io/en/latest/).

### [Pandas](https://github.com/pandas-dev/pandas/wiki/Testing)
- Pandas also uses Nose. 

### [Scrapy](https://doc.scrapy.org/en/latest/contributing.html#running-tests)
- Scrapy uses [tox](https://pypi.python.org/pypi/tox) to discover and run tests without relying on a 
`run_all_tests`-type script
