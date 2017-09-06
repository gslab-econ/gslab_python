import os
import scandir
import mmh3

from misc import check_and_expand_path, make_heading

def record_dir(start_path, name, 
               include_checksum = False,
               file_limit = 5000, 
               logpath = 'state_of_inputs.log'):
    '''
    Record relative path, size, and (optionally) checksum of all files within start_path.
    Relative paths are from start_path.
    Append info in |-delimited format to logpath below a heading made from start_path.
    '''
    check_and_expand_path(os.path.dirname(logpath))
    files_info = walk(start_path, include_checksum, file_limit)
    write_log(name, files_info, logpath)
    return None

def walk(start_path, include_checksum, file_limit, this_file_only = None):
    '''
    Walk through start_path and grab paths to all subdirs and info on all files. 
    Walk in same order as os.walk.
    Keep walking until there are no more subdirs or there's info on file_limit files.
    '''
    if os.path.isfile(start_path):
        this_file_only = os.path.abspath(start_path)
        start_path = os.path.dirname(start_path)
    dirs = [start_path]
    files_info = prep_files_info(include_checksum)
    while dirs and len(files_info) <= file_limit:
        dirs, files_info = scan_dir_wrapper(
            dirs, files_info, start_path, include_checksum, file_limit, this_file_only)
    return files_info

def prep_files_info(include_checksum):
    '''
    Create a header for the file characteristics to grab.
    '''
    files_info = [['file path', 'file size in bytes']]
    if include_checksum:
        files_info.append('MurmurHash3')
    return files_info

def scan_dir_wrapper(dirs, files_info, start_path, include_checksum, file_limit, 
                     this_file_only):
    '''
    Drop down access and output management for scan_dir. 
    Keep running the while loop in walk as directories are removed and added. 
    '''
    dir_to_scan = dirs.pop(0)
    subdirs, files_info = scan_dir(
        dir_to_scan, files_info, start_path, include_checksum, file_limit, this_file_only)
    dirs += subdirs
    return dirs, files_info

def scan_dir(dir_to_scan, files_info, start_path, include_checksum, file_limit, 
             this_file_only):
    '''
    Collect names of all subdirs and all information on files.
    '''
    subdirs = []
    entries = scandir.scandir(dir_to_scan)
    for entry in entries:
        if entry.is_dir(follow_symlinks = False):
            if '.git' in entry.path or '.svn' in entry.path:
                continue
            else:
                subdirs.append(entry.path)
        elif entry.is_file() and (not this_file_only or this_file_only == entry.path):
            f_info = get_file_information(entry, start_path, include_checksum)
            files_info.append(f_info)
            if len(files_info) == file_limit:
                break
    return subdirs, files_info
    
def get_file_information(f, start_path, include_checksum):
    '''
    Grabs path and size from scandir file object. 
    Will compute file's checksum if asked.
    '''
    f_path = os.path.relpath(f.path, start_path).strip()
    f_size = str(f.stat().st_size)
    f_info = [f_path, f_size]
    if include_checksum:
        with open(f.path, 'rU') as infile:
            f_checksum = str(mmh3.hash128(infile.read(), 2017))
        f_info.append(f_checksum)
    return f_info

def write_log(name, files_info, logpath):
    '''
    Write file information to logpath under a nice header.
    '''
    out_name = make_heading(name)
    out_files_info = ['|'.join(l) for l in files_info]
    out_files_info = '\n'.join(out_files_info)
    with open(logpath, 'ab') as f:
        f.write(out_name)
        f.write('\n')
        f.write(out_files_info)
        f.write('\n\n')
    return None
