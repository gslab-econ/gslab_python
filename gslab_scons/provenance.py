import os
import sys
import datetime
import warnings
import scandir
import mmh3
import gslab_scons.misc as misc

def make_provenance(start_path, readme_path, provenance_path, 
                    include_details     = True,
                    include_checksum    = True,
                    github_release      = None,
                    detail_limit        = 500,    # max number of files to calculate and output details for
                    external_provenance = [],     # list of external provenance files to append. If empty, automatically look for provenance files.
                    find_for_me         = False,  # automatically looks for provenance files regardless of external_provenance
                    excluded_dirs       = [],     # exclude these directories from automatic provenance look-up
                    verbose             = False): # print stuff
    '''
    Creates GSLab-approved provenance.log and place it in provenance_path.
    '''
    try:
        file_details = determine_file_details(include_details  = include_details,
                                              include_checksum = include_checksum)

        total_size, num_files, last_mtime, details = scan_wrapper(start_path       = start_path,
                                                                  include_details  = include_details,
                                                                  file_details     = file_details,
                                                                  include_checksum = include_checksum,
                                                                  detail_limit     = detail_limit, 
                                                                  verbose          = verbose)                             

        write_heading(start_path, provenance_path, github_release)
        write_directory_info(provenance_path, total_size, num_files, last_mtime)
        write_readme(readme_path, provenance_path)
        if include_details:
            write_detailed_info(provenance_path, details)
        
        write_ending(provenance_path)
        append_sub_provenance(provenance_path, external_provenance, excluded_dirs,
                              find_for_me, start_path, verbose)
    except Exception as e:
        print('make_provenance.py failed.')
        try: 
            os.remove(provenance_path)
        except OSError:
            pass
        raise e

    return None    


def determine_file_details(include_details  = True,
                           include_checksum = True):
    '''
    Determine if a checksum entry appears in the detailed file-level information.
    '''
    file_details = 'path|bytes|most recent modification time'
    if include_checksum:
        file_details = '%s|MurmurHash3' % file_details
    
    return [file_details]


def scan_wrapper(start_path, include_details, file_details, 
                 include_checksum = True,
                 detail_limit = 500,
                 verbose = False):
    '''
    Walk through start_path and get info on files in all subdirectories.
    Walk in same order as os.walk. 
    Also scan to be recurisve-like without overflowing the stack on large directories. 
    '''
    total_size, num_files, last_mtime, file_details, dirs = scan(start_path       = start_path,
                                                                 include_details  = include_details,
                                                                 include_checksum = include_details,
                                                                 detail_limit     = detail_limit,
                                                                 file_details     = file_details,
                                                                 verbose          = verbose)

    while dirs:
        new_start_path = dirs.pop(0) 
        total_size, num_files, last_mtime, file_details, dirs = scan(start_path  = new_start_path, 
                                                                include_details  = include_details,
                                                                file_details     = file_details, 
                                                                include_checksum = include_checksum, 
                                                                detail_limit     = detail_limit, 
                                                                dirs             = dirs,
                                                                total_size       = total_size,
                                                                num_files        = num_files,
                                                                last_mtime       = last_mtime,
                                                                verbose          = verbose)

    
    return total_size, num_files, last_mtime, file_details


def scan(start_path, include_details, file_details, 
         include_checksum = True,
         detail_limit     = 500,
         dirs             = [], 
         total_size       = 0,
         num_files        = 0,
         last_mtime       = 0,
         verbose          = False): 
    '''
    Grab file and create directory info from start path. 
    Also return list of unvisited subdirectories under start_path. 
    '''
    if verbose:
        print start_path

    entries = scandir.scandir(start_path)
    for entry in entries:
        if entry.is_dir(follow_symlinks = False): # Store subdirs
            dirs.append(entry.path)
        elif entry.is_file():
            # Get file info
            path = entry.path
            stat = entry.stat()
            size = stat.st_size
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            # Incorporate file info into directory info.
            total_size += size            
            num_files += 1
            last_mtime = max(last_mtime, mtime)
            # Optional detailed file information
            if include_details and (not detail_limit or num_files <= detail_limit): 
                line = '%s|%s|%s' % (path, size, mtime)
                if include_checksum:
                    with open(path, 'rU') as f:
                        checksum = str(mmh3.hash128(f.read(), 2017))
                    line = '%s|%s' % (line, checksum)
                file_details.append(line)
   
    return total_size, num_files, last_mtime, file_details, dirs


def write_heading(start_path, provenance_path, 
                  github_release = None,
                  sig = '*** GSLab directory provenance ***'):
    '''
    Write standard heading for provenance: what and for where it is. 
    '''
    out = '%s\n*** directory: %s\n' % (sig, os.path.abspath(start_path))
    if github_release != None:
        out += '\n*** GitHub release: %s \n' % github_release
    with open(provenance_path, 'wb') as f:
        f.write(out)

    return None


def write_directory_info(provenance_path, total_size, num_files, last_mtime):
    '''
    Write directory-level information to provenance. 
    '''
    out = 'total bytes: %s\n' % total_size + \
          'number of files: %s\n' % num_files + \
          'most recent modification time: %s\n' % last_mtime
    with open(provenance_path, 'ab') as f:
        f.write('\n*** Directory information\n')
        f.write(out)

    return None


def write_readme(readme_path, provenance_path):
    '''
    Writes readme to provenance.
    '''
    try:
        with open(readme_path, 'rU') as f:
            out = '%s' % f.read()
    except IOError:
        raise IOError(('Cannot read %s.\n If you are in release mode,' % readme_path) +
                      'please specify the command line argument param `readme=<README_PATH>`.' )

    with open(provenance_path, 'ab') as f:
        f.write('\n*** README verbatim\npath: %s\n' % os.path.abspath(readme_path))
        f.write(out)

    return None


def write_detailed_info(provenance_path, details):
    '''
    Writes file-level information to provenance.
    '''
    out = '%s\n' % '\n'.join(details)
    with open(provenance_path, 'ab') as f:
        f.write('\n*** File information\n')
        f.write(out)

    return None


def write_ending(provenance_path):
    with open(provenance_path, 'ab') as f:
        f.write('*' * 80 + '\n\n') # a lot of asterisks
    
    return None


def append_sub_provenance(root_provenance     = './provenance.log',
                          external_provenance = [],
                          excluded_dirs       = [],
                          find_for_me         = False,
                          start_path          = '.',
                          verbose             = False,
                          sig                 = '*** GSLab directory provenance ***'):
    
    files = misc.make_list_if_string(external_provenance)
    if files == [] or find_for_me == True: 
        pattern = 'provenance*.log'
        files += misc.finder(start_path, pattern, excluded_dirs)
    files = sorted(files)
    
    for provenance in files:
        if os.path.abspath(root_provenance) != os.path.abspath(provenance): # if this is not the root file    
            if verbose == True:
                print os.path.abspath(provenance)
        
            warning_message = '\nThe file %s does not appear to be a GSLab provenance file.\n' % provenance
            warn = False

            with open(provenance, 'rU') as f:
                content = f.readlines()
                try:
                    if content[0].strip() != sig: warn = True
                except IndexError:
                    warn = True

            with open(root_provenance, 'ab') as root_f:
                root_f.write('*** Subdirectory provenance: %s\n' % os.path.abspath(provenance))
                if warn == True:
                    warnings.warn(warning_message)
                    root_f.write(warning_message)
                root_f.write(''.join(content))
                root_f.write('\n\n')

    return None
