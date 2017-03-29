import re
import os
import sys
import _release_tools as rtools
from _exception_classes import ReleaseError


def main():
    # Preliminary checks/warnings
    inspect_repo()
    issue_size_warnings(file_MB_limit  = 2,
                        total_MB_limit = 500,
                        bytes_in_MB = 1000000)

    # Extract information about the clone from its .git directory
    repo, organisation, branch = rtools.extract_dot_git()

    # Determine the version number
    try:
        version = next(arg for arg in sys.argv if re.search("^version=", arg))
    except:
        raise ReleaseError('No version specified.')

    version = re.sub('^version=', '', version)

    # Determine whether the user has specified the no_zip option
    dont_zip    = 'no_zip' in sys.argv
    zip_release = not dont_zip

     # Read a list of files to release to Google Drive
    release_files = list()
    for root, _, files in os.walk('./release'):
        for file_name in files:
            # Do not release .DS_Store
            if not re.search("\.DS_Store", file_name):
                release_files.append(os.path.join(root, file_name))

    # Specify the local release directory
    USER = os.environ['USER']
    if branch == 'master':
        name   = repo
        branch = ''
    else:
        name = "%s-%s" % (repo, branch)
    local_release = '/Users/%s/Google Drive/release/%s/' % (USER, name)
    local_release = local_release + version + '/'
    
    rtools.release(vers              = version, 
                   DriveReleaseFiles = release_files,
                   local_release     = local_release, 
                   org               = organisation, 
                   repo              = repo,
                   target_commitish  = branch,
                   zip_release       = zip_release)


def inspect_repo():
    '''Ensure the repo is ready for release.'''
    if not rtools.up_to_date(mode = 'scons'):
        raise ReleaseError('SCons targets not up to date.')
    elif not rtools.up_to_date(mode = 'git'):
        print "Warning: `scons` has run since your latest git commit.\n"
        response = raw_input("Would you like to continue anyway? (y|n)\n")
        if response in ['N', 'n']: 
            sys.exit()


def issue_size_warnings(file_MB_limit, total_MB_limit, bytes_in_MB):
    '''Issue warnings if the files versioned in release are too large'''

    # Compile a list of files in /release/ that are not versioned.
    ignored = rtools.list_ignored_files()
    release = rtools.create_size_dictionary('./release')
    release = {k: release[k] for k in release.keys() if k not in ignored}
    versioned = dict()

    for file_name in release.keys():
        versioned[file_name] = release[file_name]

        size  = release[file_name]
        limit = file_MB_limit * bytes_in_MB

        if size > limit and file_name:
            print "Warning: the versioned file %s is larger than %d MB.\n" \
                  % (file_name, file_MB_limit)
            print "Versioning files of this size is discouraged.\n" 

            response = raw_input("Would you like to continue anyway? (y|n)\n")
            if response in ['N', 'n']: 
                sys.exit()

    total_size  = sum(versioned.values())
    total_limit = total_MB_limit * bytes_in_MB

    if total_size > total_limit:
        print "Warning: the versioned files in /release/ are together " + \
            "larger than " + str(total_MB_limit) + " MB.\n" + \
            "Versioning this much content is discouraged.\n"
        response = raw_input("Would you like to continue anyway? (y|n)\n")
        if response in ['N', 'n']: 
            sys.exit()


if __name__ == '__main__':
    main()
