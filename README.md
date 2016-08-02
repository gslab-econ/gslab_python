## GSLab Python Library 1.0

### Overview
This library contains the python tools used by GSLab. The original code in this repository is drawn from `trunk/lib/python` of the SVN repository `econ-gentzkow-stanford, revision 34,755`.

### Packages
This library contains following two packages: 
 - gslab_make for *make.py*
 - gslab_fill for *tablefill* and *textfill* 

### Installation
On command line, type `pip install --upgrade git+ssh://git@github.com/gslab-econ/gslab_python.git`

(This installation does not require git as prerequisite)

### Usage

Use the modules in the **same way** as if they were downloaded from SVN. Just remove the lines of calling SVN. 

#### Example

Take `politext/source/paper/make.py` as an example, the code should now be written as: 

`import`~~`subprocess, shutil,`~~`os`

~~`gslab_make_path = os.getenv('gslab_make_path')`~~

~~`subprocess.call('svn export --force -r 33345 ' + gslab_make_path + ' gslab_make', shell = True)`~~

`from gslab_make.py.get_externals import *`

`from gslab_make.py.make_log import *`

`from gslab_make.py.run_program import *`

`from gslab_make.py.dir_mod import *`

 ...
 
~~`get_externals('./externals.txt')`~~

~~`sys.path.append('../../external/paper/lib/python/')`~~

`from gslab_fill.py.tablefill import tablefill`

`from gslab_fill.py.textfill import textfill`
 
 ...
 
`end_make_logging('../../output/paper/make.log')`

~~`shutil.rmtree('gslab_make')`~~

`raw_input('\n Press <Enter> to exit.')`

<<<<<<< HEAD
### To-do list 

=======
(Check if this new script successfully runs on your computer and produces the right outcome for politext)

#### test

Run python interactively from terminal and type the following:
```
from eatthepie.py_module.module_test import *
from gslab_make.py.module_test import *
from political_speech.code.module_test import * 
from ebt_records.py.module_test import *
from extract_data.py.private.module_test import *
```
The results should be 
```
test success!
test success!
test success!
test success!
test sucesss!
```

### To-do list 

 - Decide which packages we do not want to include in this library
>>>>>>> 887281a78e3d8488bc3fe8d7131616f3cfb91fa6
 - Publish to PyPI


