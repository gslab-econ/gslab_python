import re
import os
import sys
import _release_tools
from _exception_classes import ReleaseError
from misc import load_yaml_value, check_and_expand_path
from provenance import make_provenance

def main(version = None,
         user_yaml = 'config_user.yaml', 
         release_files = [],
         prov_excluded_dirs = [],
         external_provenance = [],
         dont_zip = False,
         readme = None, 
         scons_local_path = 'run.py'):

    # Check if user specified a scons_local_path
    if scons_local_path == 'run.py':
        try:
            scons_local_path = next(arg for arg in sys.argv if re.search("^scons_local_path=", arg))
        except:
            pass
    inspect_repo(scons_local_path = scons_local_path)

    # Extract information about the clone from its .git directory
    try: 
        repo, organisation, branch = _release_tools.extract_dot_git()
    except: 
        try: 
            repo, organisation, branch = _release_tools.extract_dot_git(path = '../.git')
        except: 
            raise ReleaseError("Could not find .git/config in the current directory or parent directory.")

    # Determine the version number
    if version is None:
        try:
            version = next(arg for arg in sys.argv if re.search("^version=", arg))
        except:
            raise ReleaseError('No version specified.')
        version = re.sub('^version=', '', version)

    # Determine whether the user has specified the no_zip option
    if dont_zip == False:
        dont_zip = 'no_zip' in sys.argv
    zip_release = not dont_zip

    # Read a list of files to release to release_dir
    if release_files == []:
        for root, _, files in os.walk('./release'):
            for file_name in files:
                # Do not release .DS_Store
                if not re.search("\.DS_Store", file_name):
                    release_files.append(os.path.join(root, file_name))

    # Specify the local release directory
    release_dir = load_yaml_value(user_yaml, 'release_directory')
    release_dir = check_and_expand_path(release_dir)

    if branch == 'master':
        name   = repo
        branch = ''
    else:
        name = "%s-%s" % (repo, branch)
    local_release = '%s/%s/' % (release_dir, name)
    local_release = local_release + version + '/'

    # Create provenance file in ./release
    if readme is None:
        try:
            readme = next(arg for arg in sys.argv if re.search("^readme=", arg))
        except:
            readme = "readme=./README.md"
        readme = re.sub('^readme=', '', readme)

    # Check provenance options
    find_for_me = 'find_for_me' in sys.argv
    verbose     = 'verbose' in sys.argv
    try:
        detail_limit = next(arg for arg in sys.argv if re.search("^detail_limit=", arg))
    except:
        detail_limit = "detail_limit=500"
    detail_limit = re.sub('^detail_limit=', '', readme) 

    provenance_release_note = '%s, version %s' % (name, version)
    provenance_path = './release/provenance.log'
    make_provenance(start_path          = '.',
                    readme_path         = readme,
                    provenance_path     = './release/provenance.log',
                    github_release      = provenance_release_note,
                    detail_limit        = detail_limit,
                    external_provenance = external_provenance,
                    find_for_me         = find_for_me,
                    excluded_dirs       = prov_excluded_dirs,
                    verbose             = verbose) 

    # Get GitHub token:
    github_token = load_yaml_value(user_yaml, 'github_token')
    
    _release_tools.release(vers              = version, 
                           DriveReleaseFiles = release_files,
                           local_release     = local_release, 
                           org               = organisation, 
                           repo              = repo,
                           target_commitish  = branch,
                           zip_release       = zip_release,
                           github_token      = github_token,
                           provenance_path   = provenance_path)


def inspect_repo(scons_local_path = None):
    '''Ensure the repo is ready for release.'''
    if not _release_tools.up_to_date(mode = 'scons', scons_local_path = scons_local_path):
        raise ReleaseError('SCons targets not up to date.')  
    elif not _release_tools.up_to_date(mode = 'git'):
        warn = "Warning: your git working tree is not clean.\n" \
               + "End this process and run `git status` for more infomration.\n"
        print warn
        response = raw_input("Would you like to continue anyway? (y|n)\n")
        if bool(re.match('no?', response, re.IGNORECASE)):
            sys.exit()


if __name__ == '__main__':
    main()
