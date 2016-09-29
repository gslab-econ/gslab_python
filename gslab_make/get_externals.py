#! /usr/bin/env python

import os

from private.preliminaries import start_logging, end_logging, input_to_array, print_error, externals_preliminaries
from private.getexternalsdirectives import SystemDirective, SvnExportDirective, CopyDirective
import private.metadata as metadata
import private.messages as messages

######################################################
# Main Program
######################################################

def get_externals(externals_file,
                  external_dir = '@DEFAULTVALUE@',
                  makelog = '@DEFAULTVALUE@',
                  quiet = False):
    """Please see /trunk/lib/python/gslab_make/py/readme_getexternals.txt for more information."""

    # metadata.settings should not be part of argument defaults so that they can be
    # overwritten by make_log.set_option
    try:
        LOGFILE = start_logging(metadata.settings['externalslog_file'], 'get_externals.py')        
        makelog, externals, last_dir, last_rev = externals_preliminaries(makelog, externals_file, LOGFILE)
       
        for line in externals:
            try:
                directive = SystemDirective(line, LOGFILE, last_dir, last_rev)
                directive.error_check()
                directive.clean(external_dir)
                directive.issue_sys_command(quiet)

                # Save rev/dir for next line
                last_dir = directive.dir
                last_rev = directive.rev
            except:
                print_error(LOGFILE)
        end_logging(LOGFILE, makelog, 'get_externals.py')
    except Exception as errmsg:
        print "Error with get_external: \n", errmsg
