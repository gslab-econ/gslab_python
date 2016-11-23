import re
import os
import sys
from _exception_classes import ReleaseError
from _release_tools import extract_dot_git, up_to_date, release

'''
Make a release from an SCons directory using:
    python -m gslab_scons.release version=<version name here>
where <version name here> is the name of the version that
the user wishes to release. As an example, to release version
v1.2.1 of a directory, one would run:
    python -m gslab_scons.release version=v1.2.1
from the root of the directory. 
'''

if __name__ == '__main__':

    # Ensure that the directory's targets are up to date
    if not up_to_date():
        raise ReleaseError('SCons targets not up to date.')

    # Extract information about the clone's repository, organisation,
    # and branch from its .git directory
    repo, organisation, branch = extract_dot_git()

    # Determine the version number
    try:
        version = next(arg for arg in sys.argv if re.search("^version=", arg))
    except:
        raise ReleaseError('No version specified.')

    version = re.sub('^version=', '', version)

     # Read a list of files to release to Google Drive
    if not os.path.exists('release_files.txt'):
        release_files = []
    else:
        with open('release_files.txt', 'rU') as release_file:
            release_files = release_file.readlines()
    
    release_files = map(lambda x: x.strip(), release_files)

    # Specify the local release directory
    USER = os.environ['USER']
    local_release = '/Users/%s/Google Drive/release/%s/' % (USER, branch)
    local_release = local_release + version + '/'

    release(vers              = version, 
            DriveReleaseFiles = release_files,
            local_release     = local_release, 
            org               = organisation, 
            repo              = repo)
