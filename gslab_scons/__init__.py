'''
gslab_scons - a SCons builder library
=====================================

gslab_scons is a Python library containing general-purpose SCons builders 
for LyX, R, Python, and Stata. Its builders work on both Unix and Windows 
platforms. 

Please consult the docstrings of the gslab_scons builders belonging to
this module for additonal information on their functionalities.
'''

from .release import release, upload_asset
from .log import start_log, log_timestamp
import misc

from . import builders
from .builders import build_r, build_lyx, build_stata, build_tables, build_python

