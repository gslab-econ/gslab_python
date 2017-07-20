# GSLab Python Library Collection 4.0.0

Overview
--------
This repository contains the following GSLab Python libraries:
 - gslab_make
 - gslab_fill  
 - gslab_scons
 - gencat

Information about each of these packages is available in its internal documentation. 

Requirements
------------
- Python 2.7 
- `setuptools` ([installation instructions](https://packaging.python.org/installing/))
- `mock` (> 2.0.0) in order to run the unit tests 

Installation
------------

The preferred installation method is to use [pip](https://pypi.python.org/pypi/pip):
```
pip install git+ssh://git@github.com/gslab-econ/gslab_python.git@master
```
or
```
pip install git+https://git@github.com/gslab-econ/gslab_python.git@master
```
which are the SSH and HTTPS protocol versions.

Note that this installation procedure may require obtaining machine privileges through,
say, a `sudo` command. 


Alternatively, one may use:

```
python setup.py install clean
```

However, this installation method may not remove previous versions of gslab_tool.

Testing
-------

We recommend that users use [coverage](https://pypi.python.org/pypi/coverage/) 
to run this repository's unit tests. Upon installing coverage (this can be done with
pip using the command `pip install coverage`), one may test `gslab_python`'s contents
and then produce a code coverage report the commands:

```bash
python setup.py test [--include=<paths>]
```

Here, the optional `--include=` argument specifies the files whose test results
should be included in the coverage report produced by the command. 
It works as `coverage`'s argument of the same name does. The command should be
run without this option before committing to `gslab_python`.


License
-------
See [here](https://github.com/gslab-econ/gslab_python/blob/master/LICENSE.txt).

FAQs
-------

Q: What if I want to install a different branch called `dev` of `gslab_python` rather than `master`?
A: Either `git checkout dev` that branch of the repo before installing, or change `@master` to `@dev` in the `pip install` instruction.

