## GSLab Python Library 1.0.3

### Overview
This library contains the python tools used by GSLab. The original code in this repository is drawn from `trunk/lib/python` of the SVN repository `econ-gentzkow-stanford, revision 34,755`.

### Packages
This library contains following two packages: 
 - gslab_make  (for *make.py*)
 - gslab_fill  (for *tablefill* and *textfill*) 
 - gslab_scons (for using `scons`)

### Installation
First time: On command line, type `pip install gslab_tools`

Update: type `pip install gslab_tools --upgrade`

### Usage

Use the legacy modules (gslab_make, gslab_fill) in the **same way** as if they were downloaded from SVN. Just remove the lines of calling SVN. 

#### Example

Take [politext/source/paper/make.py](https://github.com/TaddyLab/politext/blob/master/source/paper/make.py) as an example, the code should now be written as: 

`import`~~`subprocess, shutil,`~~`os`

~~`gslab_make_path = os.getenv('gslab_make_path')`~~

~~`subprocess.call('svn export --force -r 33345 ' + gslab_make_path + ' gslab_make', shell = True)`~~

`from gslab_make.get_externals import *`

`from gslab_make.make_log import *`

`from gslab_make.run_program import *`

`from gslab_make.dir_mod import *`

 ...
 
~~`get_externals('./externals.txt')`~~

~~`sys.path.append('../../external/paper/lib/python/')`~~

`from gslab_fill.tablefill import tablefill`

`from gslab_fill.textfill import textfill`
 
 ...
 
`end_make_logging('../../output/paper/make.log')`

~~`shutil.rmtree('gslab_make')`~~

`raw_input('\n Press <Enter> to exit.')`

#### Documentation

After importing a module, one can use `help()` to see its documentation, for example:
`help(gslab_fill.tablefill)`

### Updating procedures

* Put `__init__.py` in each new subdirectories (except test folders)
* Run `make.py` in each package to test if the new version is working appropriately 
* Update `README.md` and `setup.py` to contains the information about this new version
* Check that the local environment for publishing is ready (see [here](https://www.codementor.io/python/tutorial/host-your-python-package-using-github-on-pypi))
   * The username and password for PyPI are stored in GSLab Evernote notebook
* Push everything to `gslab_python` repo in github
* Release on github with the tag version to be the version number of this package 
* Copy the download link from github release page and paste it in `setup.py`
* Type the following to upload the new version to PyPI test: 
   * `python setup.py register -r pypitest`
   * `python setup.py sdist upload -r pypitest`
* Now type the following to upload the new version to PyPI: 
   * `python setup.py register -r pypi`
   * `python setup.py sdist upload -r pypi`





