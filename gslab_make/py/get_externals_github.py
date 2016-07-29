#! /usr/bin/env python
import os
import getpass


from private.preliminaries import start_logging, end_logging, input_to_array, print_error, externals_preliminaries
from private.getexternalsdirectives import SystemDirective
import private.metadata as metadata
import private.messages as messages

######################################################
# Main Program
######################################################

def get_externals_github(externals_file,
                  external_dir = '@DEFAULTVALUE@',
                  makelog = '@DEFAULTVALUE@',
                  quiet = False):
    """Please see /trunk/lib/python/gslab_make/py/readme_getexternalsgithub.txt for more information."""

    # metadata.settings should not be part of argument defaults so that they can be
    # overwritten by make_log.set_option
    try:
        # Request Token
        token = getpass.getpass("Enter github token and then press enter: ") 
        LOGFILE = start_logging(metadata.settings['githublog_file'], 'get_externals_github.py')        
        makelog, externals, last_dir, last_rev = externals_preliminaries(makelog, externals_file, LOGFILE)

        for line in externals:
            try:                          
                directive = SystemDirective(line, LOGFILE, last_dir, last_rev, token = token)
                directive.error_check()
                directive.clean(external_dir)
                directive.issue_sys_command(quiet)
            except:
                print_error(LOGFILE)
        end_logging(LOGFILE, makelog, 'get_externals_github.py')       
    except Exception as errmsg:
        print "Error with get_externals_github: \n", errmsg
        
        
