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
    '''Fetch external files

    Description:
    This function interprets a formatted text document listing files 
    to be exported via SVN or a system copy command.

    Syntax:
    get_externals(externals_file [, externals_dir [, makelog [, quiet]]])

    Usage:
    The `externals_file` argument should be the path of a tab-delimited text 
    file containing information on the external files that the function call
    should retrieve. This file needs to rows of numbers or characters, delimited 
    by either tabs or 4 spaces,one for each file to be exported via svn.
    The proper format is: rev   dir file    outdir  outfile notes

        ### Column descriptions:
        *  rev 
          * Revision number of the file/directory in integer format. 
            If left blank along with directory column, get_externals.py will 
            read the last specified revision number. If copying from a shared 
            drive rather than the repository, list revision number as COPY.
        *  dir
          *  Directory of the file/directory requested. As described above, 
             %xxx% placemarkers are substituted in from predefined values in 
             metadata.py. If left blank along with revision column, 
             get_externals.py will read the last specified directory. 
        *  file 
          *  Name of the file requested. If entire directory is required, leave 
             column as a single *. If a file name wildcard is required place 
             single * within filename. get_externals.py will attempt to screen
              out bad file names. Cannot be left blank.
        *  outdir   
          *  Desired output directory of the exported file/directory. 
             Typically of the form ./subdir/. If left blank, will be 
             filled with the first level of the externals relative path. 
        *  outfile 
          *  Desired output name of the exported file/directory. If left as 
             double quotes, indicates that it should have the same name. 
             Adding a directory name that is different from the default """" 
             will place this subdirectory within the outdir. Additionally, 
             get_externals can assign a prefix tag to exported file collections, 
             either through a folder export, or a wildcard call; it does so 
             when the outfile column contains text of the pattern '[prefix]*', 
             where the prefix [prefix] will be attached to exported files. 
        *  notes
          *  Optional column with notes on the export. get_externals.py ignores this, but logs it.
                
        Example of externals.txt:
        ```
        rev dir file    outdir  outfile notes
        2    %svn%/directory/  *   ./destination_directory/ """"
        COPY    %svn%/other_directory/   my_file.txt  .   """"    
        ```

    The destination directory is specified by an optional second 
    parameter whose default value is "../external". The log file produced by 
    get_externals is automatically added to an optional third parameter 
    whose default value is '../output/make.log'. 

    The fourth argument, quiet, is by default False.  Setting this argument to 
    True suppresses standard output and errors from SVN. 

    '''
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
