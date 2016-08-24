## GSLab Python Library 1.0.5

### Overview
This library contains the python tools used by GSLab. The original code in this repository is drawn from `trunk/lib/python` of the SVN repository `econ-gentzkow-stanford, revision 34,755`.

### Modules
This library contains following two modules: 
 - gslab_make  (for *make.py*)
 - gslab_fill  (for *tablefill* and *textfill*) 
 - gslab_scons (for using `scons`)

### Installation
First time: On command line, enter `pip install gslab_tools`.

Update: Enter `pip install gslab_tools --upgrade`.

### Usage

We can use our legacy modules (gslab_make, gslab_fill) in the **same way** as if they were downloaded from SVN. When uodating code, we should remove the lines downloading content from SVN. 

#### Example

As an example of how to update code to use this module's Python utilities rather than retrieve them from SVN, consider the following truncated script (taken from  [politext/source/paper/make.py](https://github.com/TaddyLab/politext/blob/master/source/paper/make.py):

```Python
import subprocess
import shutil
import os
gslab_make_path = os.getenv('gslab_make_path')
subprocess.call('svn export --force -r 33345 ' + gslab_make_path + ' gslab_make', shell = True)
from gslab_make.py.get_externals import *
from gslab_make.py.make_log import *
from gslab_make.py.run_program import *
from gslab_make.py.dir_mod import *

# ...
# Excluded code
# ...

get_externals('./externals.txt')
sys.path.append('../../external/paper/lib/python/')
from gslab_misc.py.tablefill import tablefill
from gslab_misc.py.textfill import textfill
 
# ...
# Excluded code
# ...
 
end_make_logging('../../output/paper/make.log')

shutil.rmtree('gslab_make')
raw_input('\n Press <Enter> to exit.')
```

After installing `gslab_tools` using pip, would can safely remove the lines that download the GSLab Python utilities from SVN and a few others. Our revised code should look like (without the comments inserted for clarity):

```Python
# The only package we need to load now is os
import os
# We can load our Python make functions without downloading them.
# Also, we no longer need the get_externals submodule
# Last, note that we can (and must) remove 'py.' from our module path
from gslab_make.make_log import *
from gslab_make.run_program import *
from gslab_make.dir_mod import *

# ...
# Excluded code
# ...

# We can remove the "get externals" lines
from gslab_fill.tablefill import tablefill
from gslab_fill.textfill import textfill

# ...
# Excluded code
# ...

end_make_logging('../../output/paper/make.log')

raw_input('\n Press <Enter> to exit.')
```


#### Documentation

After importing a module, one can use `help()` to see its documentation. For example, `help(gslab_fill.tablefill)` will provide the user with information on our `table_fill` function.

### Updating procedures

* Ensure that `__init__.py` has been placed in each new subdirectory, excluding test folders,
* Run `make.py` in each package to test if the new version is working appropriately,
* Update `README.md` and `setup.py` with information about the current version of gslab_tools,
* Check that you have set up your PyPI publishing profile (see [here](https://www.codementor.io/python/tutorial/host-your-python-package-using-github-on-pypi))
   * Note: the username and password for PyPI are stored in GSLab Evernote notebook.
* Push changes to `README.md` and `setup.py` everything to the `gslab_python` Github repository;
* Release the current version of gslab_tools on Github, setting the tag version to be the version number of this package;
* Copy the download link from GitHub release page and paste it into `setup.py`'s `download_url` field;
* Enter the following at the command line to upload the new version to PyPI test: 
   * `python setup.py register -r pypitest`
   * `python setup.py sdist upload -r pypitest`
* Now enter the following to upload the new version to PyPI: 
   * `python setup.py register -r pypi`
   * `python setup.py sdist upload -r pypi`
 





