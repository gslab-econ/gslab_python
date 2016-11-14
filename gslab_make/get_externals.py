#! /usr/bin/env python

import os
import private.preliminaries as prelim
import private.metadata as metadata
import private.messages as messages

from private.getexternalsdirectives import SystemDirective

def get_externals(externals_file,
                  external_dir = '@DEFAULTVALUE@',
                  makelog      = '@DEFAULTVALUE@',
                  quiet        = False):
    '''Fetch external files from SVN'''

    # metadata.settings should not be part of argument defaults so that they can be
    # overwritten by make_log.set_option
    try:
        LOGFILE = prelim.start_logging(metadata.settings['externalslog_file'], 'get_externals.py')        
        makelog, externals, last_dir, last_rev =  \
            prelim.externals_preliminaries(makelog, externals_file, LOGFILE)
       
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
                prelim.print_error(LOGFILE)
        prelim.end_logging(LOGFILE, makelog, 'get_externals.py')

    except Exception as errmsg:
        print "Error with get_external: \n", errmsg
