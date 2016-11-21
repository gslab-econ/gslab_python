#! /usr/bin/env python

import os
import getpass
import private.preliminaries as prelim
import private.metadata as metadata
import private.messages as messages
from private.getexternalsdirectives import SystemDirective


def get_externals_github(externals_file, external_dir = '@DEFAULTVALUE@',
                         makelog = '@DEFAULTVALUE@', quiet = False):
    '''Fetch external files from GitHub

    Description:
    This function retrieves files from GitHub as specified by a formatted text
    document indicated as an argument. 
    get_externals_github is only intended to download assets from releases.
    It cannot download the release source code or other assets not contained 
    within a release.

    Usage:
    - This function's usage largely follows that of get_externals(). Instead of 
      rading
    - get_externals_github is only intended to download assets from releases.
      It cannot download the release source code or other assets not contained 
      within a release.

    File format of a `externals_file`:
    This file needs to rows of numbers or characters, delimited by either tabs or 
    4 spaces, one for each file to be exported via GitHub.
    The proper column format is: url   outdir  outfile notes
    
    Column descriptions:
    *  url  
      *  Download url for the file in a specific GitHub release. The url given 
         should be the complete url.
    *  outdir 
      *  Desired output directory of the exported file/directory. Typically of the form 
         ./subdir/. If left blank, will be filled with the first level of the externals 
         relative path. 
    *  outfile 
      *  Desired output name of the exported file/directory. If left as double quotes, 
         indicates that it should have the same name as the asset name in GitHub. 
    *  notes 
      *  Optional column with notes on the export. get_externals_github.py ignores this,
         but logs it.

    Example of externals_github.txt:

    ```
    url outdir  outfile notes   
    https://github.com/TestUser/TestRepo/releases/download/v1.0/document.pdf    ./  """"
    https://github.com/TestUser/TestRepo/releases/download/AlternativeVersion/other_document.pdf    ./  """"
    ```
    '''
    try:
        # Request Token
        token = getpass.getpass("\nEnter a valid GitHub token and then press enter: ") 

        LOGFILE = prelim.start_logging(metadata.settings['githublog_file'], 
                                      'get_externals_github.py')        
        makelog, externals, last_dir, last_rev = \
            prelim.externals_preliminaries(makelog, externals_file, LOGFILE)

        for line in externals:
            try:                          
                directive = SystemDirective(line, LOGFILE, last_dir, last_rev, 
                                            token = token)
                directive.error_check()
                directive.clean(external_dir)
                directive.issue_sys_command(quiet)
            except:
                prelim.print_error(LOGFILE)
        
        prelim.end_logging(LOGFILE, makelog, 'get_externals_github.py')       
    
    except Exception as errmsg:
        print "Error with get_externals_github: \n", errmsg
        