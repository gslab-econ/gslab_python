'''
gslab_scons - a SCons builder library
=====================================

gslab_scons is a Python library containing general-purpose SCons builders 
for LyX, R, Python, and Stata. Its builders work on both Unix and Windows 
platforms. 

Please consult the docstrings of the following gslab_scons builders for
additional information on their functionalities:
- build_lyx
- build_r
- build_python
- build_tables
- build_r
- build_stata

In general, the source code file (e.g. `.do` for Stata) must be listed as 
the first argument in source when calling builders from SConscript.
'''

from .release import release, upload_asset
from .log import start_log, log_timestamp
from ._exceptions import BadExecutableError, BadExtensionError, LFSError
import misc

from . import builders
from .builders import build_r, build_lyx, build_stata, build_tables, build_python

