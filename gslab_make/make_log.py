#! /usr/bin/env python
import sys
import subprocess
import shutil
import os
import datetime
import re
import string

import private.messages as messages
import private.metadata as metadata
from private.preliminaries import print_error, files_list
from dir_mod import delete_files, list_directory
from private.exceptionclasses import CustomError, CritError, SyntaxError, LogicError

#== Set default options ==============================

def set_option(**kwargs):
    """This function takes a dictionary as input and overwrites the default values
    of the settings in metadata. The key identifies the setting to be changed, 
    and the value will be the new default value of that setting.
    The keys should match with the ones identified by metadata.setting (see above).

    This function can be used to overwrite the default setting options. All other 
    functions that come after it will not have to re-specify those options. For example:
    
    e.g.
    set_option(makelog = 'make.log', temp_dir = '', output_dir = './log', 
               external_dir = './external', manifest = './manifest.log', 
               externalslog = './log/externals.log')

    - Each of the above is optional. For all keys, "_dir" and "_file" are optional.
    """

    try:
        dict((k.lower(), v) for k, v in kwargs.iteritems())

        keylist = metadata.settings.keys()
        
        file_keylist = [ k for k in keylist if k.endswith('file') ]
        dir_keylist = [ k for k in keylist if k.endswith('dir') ]

        # filekey or filekey without "_file" should both work
        n = len("_file")
        for filekey in file_keylist:
            if filekey in kwargs.keys():
                metadata.settings[filekey] = kwargs[filekey]
                if filekey[:-n] in kwargs.keys():
                    raise SyntaxError( messages.syn_error_dupkeys % (filekey, filekey[:-n]) )
            elif filekey[:-n] in kwargs.keys():
                metadata.settings[filekey] = kwargs[filekey[:-n]]

        # dirkey or dirkey without "_dir" should both work
        n = len("_dir")
        for dirkey in dir_keylist:
            if dirkey in kwargs.keys():
                metadata.settings[dirkey] = kwargs[dirkey]
                if dirkey[:-n] in kwargs.keys():
                    raise SyntaxError( messages.syn_error_dupkeys % (dirkey, dirkey[:-n]) )
            elif dirkey[:-n] in kwargs.keys():
                metadata.settings[dirkey] = kwargs[dirkey[:-n]]
    except Exception as errmsg:
        print "Error with set_option: \n", errmsg


#== Logging ==========================================
def start_make_logging(makelog = '@DEFAULTVALUE@'):
    """Start "makelog" log file with time stamp.
    
    Notes:
    -  This is usually put at the start of make.py. To start the default 
       '../output/make.log' with time stamp, use: `start_make_logging()`
    - If one would like to store the log file in './make.log' instead, use:
      `start_make_logging('make.log', '', '')`
    """

    if makelog == '@DEFAULTVALUE@':
        makelog = metadata.settings['makelog_file']

    metadata.makelog_started = True

    print "\nStart log file: ", makelog

    makelog = re.sub('\\\\', '/', makelog)

    try:
        LOGFILE = open(makelog, 'wb')
    except Exception as errmsg:
        raise CritError((messages.crit_error_log % makelog) + '\n' + str(errmsg))
        
    try:
        # Add time stamp
        time_begin = datetime.datetime.now().replace(microsecond = 0)
        sys.stderr = LOGFILE
        working_dir = os.getcwd()
        print >> LOGFILE, messages.note_makelogstart, time_begin, working_dir, '\n\n'

        LOGFILE.close()
    except Exception as errmsg:
        print "Error with start_make_logging: \n", errmsg

def end_make_logging(makelog = '@DEFAULTVALUE@'):
    """End "makelog" log file with time stamp.

    - To end make.py by putting the time stamp in the default 
      '../output/make.log', use: `end_make_logging()`

    - If the log file is different, we have to specify it:
      `end_make_logging('logfile.txt')`
    """

    if makelog == '@DEFAULTVALUE@':
        makelog = metadata.settings['makelog_file']

    if not (metadata.makelog_started and os.path.isfile(makelog)):
        raise CritError(messages.crit_error_nomakelog % makelog)

    print "\nEnd log file: ", makelog

    makelog = re.sub('\\\\', '/', makelog)
    try:
        LOGFILE = open(makelog, 'ab')
    except Exception as errmsg:
        raise CritError((messages.crit_error_log % makelog) + '\n' + str(errmsg))
    time_end = datetime.datetime.now().replace(microsecond = 0)
    print >> LOGFILE, messages.note_makelogend, time_end
    LOGFILE.close()


#== Additions and deletions from logs ================
def add_log(*args, **kwargs):
    """Add log files in "*arg" list to "makelog" log file.

    - If there are log files created inside scripts (for example 
      from a Perl or Python script), and we want to append their content 
      to the end of the default log file (usually '../output/make.log'), we
      would use: `add_log('../output/analysis.log', '../output/another_log.log')`
    - The number of log arguments can vary. If the log files don't actually exist, 
      errors will be printed to the common log file.
    - If we want to append content of log files to a different log file than the 
      default, we would use: 
     `add_log('../output/analysis.log', '../output/another_log.log', makelog = '../different.log')`
    """

    if 'makelog' in kwargs.keys():
        makelog = kwargs['makelog']
    else:
        makelog = metadata.settings['makelog_file']

    if not (metadata.makelog_started and os.path.isfile(makelog)):
        raise CritError(messages.crit_error_nomakelog % makelog)

    print "\nAdd log file(s) to: ", makelog

    makelog = re.sub('\\\\', '/', makelog)
    try:
        LOGFILE = open(makelog, 'ab')
    except Exception as errmsg:
        raise CritError((messages.crit_error_log % makelog) + '\n' + str(errmsg))

    try:
        for log in args:
            log = re.sub('\\\\', '/', log)
            if not os.path.isfile(log):
                print >> LOGFILE, messages.note_nofile % log
            else:
                LOGFILE.write(open(log, 'rU').read())
    except:
        print_error(LOGFILE)

    LOGFILE.close()


def del_log(*args, **kwargs):
    """Delete log files

    This function deletes each of the log files listed in "*arg" list.
    Errors are printed to `makelog` log file.

    - After we append the various log files to the common one using add_log, we may 
      want to delete the extra ones to clean up the output folder. Here is the command:
        `del_log('../output/analysis.log', '../output/another_log.log')
    - If variable 'makelog' is not defined in kwargs, errors from del_log will be printed 
      to the default makelog (usually '../output/make.log'). If we want to specify a 
      different log to which we print the errors:
      `del_log('../output/analysis.log', '../output/another_log.log', 
               makelog = '../different.log')`
    """

    if 'makelog' in kwargs.keys():
        makelog = kwargs['makelog']
    else:
        makelog = metadata.settings['makelog_file']

    if not (metadata.makelog_started and os.path.isfile(makelog)):
        raise CritError(messages.crit_error_nomakelog % makelog)

    print "\nDelete log file(s)"

    makelog = re.sub('\\\\', '/', makelog)
    try:
        LOGFILE = open(makelog, 'ab')
    except Exception as errmsg:
        raise CritError((messages.crit_error_log % makelog) + '\n' + str(errmsg))

    try:
        for log in args:
            log = re.sub('\\\\', '/', log)
            if os.path.isfile(log):
                os.remove(log)
            else:
                print >> LOGFILE, messages.note_nofile % log
    except:
        print_error(LOGFILE)

    LOGFILE.close()


#== Log file information and file heads ==============
def make_output_local_logs (output_local_dir = '@DEFAULTVALUE@',
           output_dir = '@DEFAULTVALUE@',
           stats_file = '@DEFAULTVALUE@', 
           heads_file = '@DEFAULTVALUE@',
           recur_lim = 1):
    '''Creates stats_file and heads_file for the files in "output_local_dir" up to a 
    directory depth of "recur_lim". (Calls make_stats_log and make_heads_log)

    Syntax:
    make_output_local_logs([output_local_dir [, output_dir [, stats_file 
                           [, heads_file [, recur_lim]]]]])

    Notes:
    - In svn_derived_local directories, the output_local directory is not committed to the
      repository, but it still contains important output. make_output_local_logs is called
      after the output_local content has been created to log the most important features.
    - Normally, the call can just be make_output_local_logs(), but to choose values other
      than the defaults:
      ``` 
      make_output_local_logs(output_local_dir = '../other_output_local/', 
                             output_dir = '../output_logs_dir/', 
                             stats_file = 'other_stats.log', 
                             heads_file = 'other_heads.log',
                             recur_lim = False)
      ```                                               
    - This will log all the files in '../other_output_local/' and all its subdirectories
      (there is no depth limit because recur_lim == False). The logs would be named 
      'other_stats.log' and 'other_heads.log' and would be saved in '../output_logs_dir/'.
    '''    
    if output_local_dir == '@DEFAULTVALUE@':
        output_local_dir = metadata.settings['output_local_dir']
    if output_dir == '@DEFAULTVALUE@':
        output_dir = metadata.settings['output_dir']
    if stats_file == '@DEFAULTVALUE@':
        stats_file = metadata.settings['stats_file']
    if heads_file == '@DEFAULTVALUE@':
        heads_file = metadata.settings['heads_file']

    sorted_files = files_list(output_local_dir, recur_lim)

    make_stats_log(output_dir, stats_file, sorted_files)
    make_heads_log(output_dir, heads_file, sorted_files)
    

def make_stats_log (output_dir, stats_file, all_files):
    """
    Create a log file at "stats_file" in "output_dir" of statistics of the 
    files listed in "all_files". The statistics are (in order): file name, date
    and time last modified, and file size.

    Syntax:
    make_stats_log(output_dir, stats_file, all_files)

    Note:
    -  This is called by make_output_local_logs, and will not normally 
       be called independently.
    """
    
    if stats_file == '':
        return

    stats_path = os.path.join(output_dir, stats_file)      
    stats_path = re.sub('\\\\', '/', stats_path)
    header = "file name\tlast modified\tfile size"
    
    if not os.path.isdir(os.path.dirname(stats_path)):
        os.makedirs(os.path.dirname(stats_path))
    STATSFILE = open(stats_path, 'w+')
    print >> STATSFILE, header        

    for file_name in all_files:
        stats = os.stat(file_name)
        last_mod = datetime.datetime.utcfromtimestamp(round(stats.st_mtime))
        file_size = stats.st_size

        print >> STATSFILE, "%s\t%s\t%s" % (file_name, last_mod, file_size)
    STATSFILE.close()


def make_heads_log (output_dir, heads_file, all_files, head_lines = 10):
    """
    Create a log file at "heads_file" in "output_dir" of the first 
    "head_lines" lines of each file listed in "all_files".

    Syntax:
    make_heads_log(output_dir, heads_file, all_files, head_lines)

    Note:
    -  This is called by make_output_local_logs, and will not normally 
       be called independently.
    """
    
    if heads_file == '':
        return
    
    heads_path = os.path.join(output_dir, heads_file)      
    heads_path = re.sub('\\\\', '/', heads_path)
    header = "File headers"

    if not os.path.isdir(os.path.dirname(heads_path)):
        os.makedirs(os.path.dirname(heads_path))
    HEADSFILE = open(heads_path, 'w+')
    print >> HEADSFILE, header
    print >> HEADSFILE, "\n%s\n" % ("-" * 65)        
    
    for file_name in all_files:
        print >> HEADSFILE, "%s\n" % file_name
        try:
            f = open(file_name)
        except:
            f = False
            print >> HEADSFILE, "Head not readable"
        
        if f:       
            for i in range(head_lines):
                try:
                    line = f.next().strip()
                    cleaned_line = filter(lambda x: x in string.printable, line)
                    print >> HEADSFILE, cleaned_line
                except:
                    break

        print >> HEADSFILE, "\n%s\n" % ("-" * 65)
            
    HEADSFILE.close()
