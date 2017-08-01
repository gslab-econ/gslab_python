from __future__ import division

import os
import re
import sys
import subprocess
from _exception_classes import ReleaseError


def issue_size_warnings(look_in = ['source', 'raw', 'release'],
                        file_MB_limit = 2, 
                        total_MB_limit = 500):
    '''Issue warnings if versioned files are large'''
    bytes_in_MB = 1000000
    # Compile a list of files that are not versioned.
    ignored   = list_ignored_files(look_in)
    versioned = create_size_dictionary(look_in)
    versioned = {k: versioned[k] for k in versioned.keys() if k not in ignored}

    for file_name in versioned.keys():
        size  = versioned[file_name]
        limit = file_MB_limit * bytes_in_MB

        if size > limit and file_name:
            size_in_MB = size / bytes_in_MB
            print _red_and_bold("Warning:") + \
                  " the versioned file %s "  % file_name  + \
                  "(size: %.02f MB)\n\t"     % size_in_MB + \
                  "is larger than %.02f MB." % file_MB_limit
            print "Versioning files of this size is discouraged.\n" 

    total_size  = sum(versioned.values())
    total_limit = total_MB_limit * bytes_in_MB

    if total_size > total_limit:
        total_size_in_MB = total_size / bytes_in_MB
        print _red_and_bold("Warning:") + \
              " the total size of versioned files " + \
              "in the directories %s\n\tis "      % str(look_in) + \
              "%.02f MB, which exceeds "          % total_size_in_MB + \
              "our recommended limit of %f.02 MB" % total_MB_limit
        print "Versioning this much content is discouraged.\n"


def _red_and_bold(warning):
    '''
    Make a string bold and red when printed to the terminal
    http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    '''
    red = '\033[91m' 
    bold = '\033[1m'
    end_formatting = '\033[0m' 
    return (red + bold) + warning + (end_formatting)


def list_ignored_files(look_in):
    '''List files ignored by git 

    This function returns a list of the files in the directory
    given by the dir_path argument that are ignored by git. 
    '''
    # Produce a listing of files and directories ignored by git
    message = subprocess.check_output('git status --ignored', shell = True)
    message = message.split('\n')
    message = map(lambda s: s.strip(), message)

    try:
        ignored_line = message.index('Ignored files:')
    except ValueError:
        # If the git status message lists no ignored files, return empty list
        return []

    # Loop through the listing of ignored paths, classifying them
    # as files or directories
    ignore_dirs  = []
    ignore_files = []
    for line in message[ignored_line:len(message)]:
        as_path = os.path.normpath(line)

        # Only check for ignored files in the specified "look_in" directories
        superpaths = [d for d in look_in if _is_subpath(as_path, d)]
        if len(superpaths) == 0:
            continue

        if os.path.isdir(line):
            ignore_dirs.append(line)
        elif os.path.isfile(line):
            ignore_files.append(line)

    # Find the paths of files in the ignored directories
    for directory in ignore_dirs:
        for dname, _, fnames in os.walk(directory):
            files = [os.path.join(dname, s) for s in fnames]
            files = [os.path.normpath(f) for f in files]
            ignore_files += files

    return ignore_files


def _is_subpath(inner, outer):
    '''
    Check that `inner` is a subdirectory or file in the directory
    specified by `outer`.
    '''
    outer = os.path.abspath(outer)
    inner = os.path.abspath(inner)
    return bool(re.search('^%s' % outer, inner))


def create_size_dictionary(dirs):
    '''
    This function creates a dictionary reporting the sizes of
    files in the directoriries specified by `dirs`, a list of strings. 
    The filenames are the dictionary's keys; their sizes in 
    bytes are its values. 
    '''
    size_dictionary = dict()

    for path in dirs:
        if not os.path.isdir(path):
            print("WARNING: '%s' is not an existing directory." % path)
            continue
        for root, _, files in os.walk(path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                size      = os.path.getsize(file_path)
                size_dictionary[os.path.normpath(file_path)] = size

    return size_dictionary

