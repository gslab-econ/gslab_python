GSLab Python Library Collection 3.0.3
=====================================

Overview
--------
This repository contains the following GSLab Python libraries:
 - gslab_make
 - gslab_fill  
 - gslab_scons
 - gencat

Information about each of these packages is available in its internal documentation. 

Note: In order to run the unit tests, `mock` (version 2.0.0 or higher) needs to be installed.

Installation
------------
To install this repository's Python libraries, run the `setup.py` script at its root
with the command:

```
python setup.py install clean
```

where the optional clean command deletes files used in installating the libraries
after installation is complete.

One can use `pip` to assist with this installation procedure by using the commands:
```
pip install git+ssh://git@github.com/gslab-econ/gslab_python.git
```
or
```
pip install git+https://git@github.com/gslab-econ/gslab_python.git
```
which are the SSH and HTTPS protocol versions.

Note that this installation procedure may require obtaining machine privileges through,
say, a `sudo` command. 


Testing
-------

We recommend that users use [coverage](https://pypi.python.org/pypi/coverage/) 
to run this repository's unit tests. Upon installing coverage (this can be done with
pip using the command `pip install coverage`), one may test `gslab_python`'s contents
and then produce a code coverage report the commands:

```bash
coverage run setup.py test
coverage report -m
```

License
-------
See [here](https://github.com/gslab-econ/gslab_python/blob/master/LICENSE.txt).
