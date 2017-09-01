import requests
import getpass
import re
import json
import time
import os
import sys
import shutil
import subprocess

from _exception_classes import ReleaseError

def release(vers, org, repo,
            DriveReleaseFiles = [],  
            local_release     = '',  
            target_commitish  = '', 
            zip_release       = True,
            github_token      = None,
            provenance_path   = './release/provenance.log'):
    '''Publish a release

    Parameters
    ----------
    env: an SCons environment object
    vers: the version of the release
    DriveReleaseFiles a optional list of files to be included in a
        release to drive (e.g. DropBox or Google Drive).
    local_release: The path of the release directory on the user's computer.
    org: The GtHub organisaton hosting the repository specified by `repo`.
    repo: The name of the GitHub repository from which the user is making
        the release.
    '''
    # Check the argument types

    if bool(github_token) is False:
        github_token = getpass.getpass("Enter a GitHub token and then press enter: ") 
    
    tag_name = vers
    
    releases_path = 'https://%s:@api.github.com/repos/%s/%s/releases' \
                    % (github_token, org, repo)
    session       = requests.session()

    # Create release
    payload = {'tag_name':         tag_name, 
               'target_commitish': target_commitish, 
               'name':             tag_name, 
               'body':             '', 
               'draft':            'FALSE', 
               'prerelease':       'FALSE'}

    json_dump = json.dumps(payload)
    json_dump = re.sub('"FALSE"', 'false', json_dump)
    posting   = session.post(releases_path, data = json_dump)
    # Check that the GitHub release was successful
    try:
        posting.raise_for_status()
    except requests.exceptions.HTTPError:
        message  = "We could not post the following json to the releases path \n" 
        message  = message + ("https://YOURTOKEN:@api.github.com/repos/%s/%s/releases \n" % (org, repo))
        message  = message + "The json looks like this:"
        print(message)
        for (k,v) in payload.items():
            print(" '%s' : '%s' " % (k,v))
        raise requests.exceptions.HTTPError

    # Release to drive
    if bool(DriveReleaseFiles):
        # Delay
        time.sleep(1)
    
        if isinstance(DriveReleaseFiles, basestring):
            DriveReleaseFiles = [DriveReleaseFiles]

        # Get release ID
        json_releases  = session.get(releases_path)
        # Check that the request was successful
        json_releases.raise_for_status()

        json_output    = json_releases.content
        json_split     = json_output.split(',')
        # The id for each tag appears immediately before its tag name
        # in the releases json object.
        tag_name_index = json_split.index('"tag_name":"%s"' % tag_name)
        release_id     = json_split[tag_name_index - 1].split(':')[1]
    
        # Get root directory name on drive
        path       = local_release.split('/')
        drive_name = path[-2]
        dir_name   = path[-1]

        if not os.path.isdir(local_release):
            os.makedirs(local_release)
       
        # If the files released to drive are to be zipped,
        # specify their copy destination as an intermediate directory
        if zip_release:
            archive_files = 'release_content'
            if os.path.isdir(archive_files):
                shutil.rmtree(archive_files)
            os.makedirs(archive_files)

            destination_base = archive_files
            drive_header = '%s: release/%s/%s/release_content.zip' % \
                            (drive_name, dir_name, vers)
        # Otherwise, send the release files directly to the local release
        # drive directory
        else:
            destination_base = local_release
            drive_header = '%s:' % drive_name

        for path in DriveReleaseFiles:
            file_name   = os.path.basename(path)
            folder_name = os.path.dirname(path)
            destination = os.path.join(destination_base, folder_name)
            if not os.path.isdir(destination):
                os.makedirs(destination)
            shutil.copy(path, os.path.join(destination, file_name))
        
        if zip_release:
            shutil.make_archive(archive_files, 'zip', archive_files)
            shutil.rmtree(archive_files)
            shutil.move(archive_files + '.zip', 
                        os.path.join(local_release, 'release.zip'))

        if not zip_release:
            make_paths = lambda s: 'release/%s/%s/%s' % (dir_name, vers, s)
            DriveReleaseFiles = map(make_paths, DriveReleaseFiles)

        with open('drive_assets.txt', 'wb') as f:
            f.write('\n'.join([drive_header] + DriveReleaseFiles))

        upload_asset(github_token = github_token, 
                     org          = org, 
                     repo         = repo, 
                     release_id   = release_id, 
                     file_name    = 'drive_assets.txt')

        os.remove('drive_assets.txt')

        upload_asset(github_token = github_token, 
                     org          = org,    
                     repo         = repo, 
                     release_id   = release_id, 
                     file_name    = provenance_path)


def upload_asset(github_token, org, repo, release_id, file_name, 
                 content_type = 'text/markdown'):
    '''
    This function uploads a release asset to GitHub.

    --Parameters--
    github_token: a GitHub token
    org: the GitHub organisation to which the repository associated
        with the release belongs
    repo: the GitHub repository associated with the release
    release_id: the release's ID
    file_name: the name of the asset being released
    content_type: the content type of the asset. This must be one of
        types accepted by GitHub. 
    '''
    session = requests.session()

    if not os.path.isfile(file_name):
        raise ReleaseError('upload_asset() cannot find file_name')

    files  = {'file' : open(file_name, 'rU')}
    header = {'Authorization': 'token %s' % github_token, 
              'Content-Type':  content_type}
    path_base   = 'https://uploads.github.com/repos'
    upload_path = '%s/%s/%s/releases/%s/assets?name=%s' % \
                  (path_base, org, repo, release_id, file_name)
 
    r = session.post(upload_path, files = files, headers = header)
    return r.content


def up_to_date(mode = 'scons', directory = '.'):
    '''
    If mode = scons, this function checks whether the targets of a 
    directory run using SCons are up to date. 
    If mode = git, it checks whether the directory's sconsign.dblite has
    changed since the latest commit.
    '''
    if mode not in ['scons', 'git']:
        raise ReleaseError("up_to_date()'s mode argument must be "
                           "'scons' or 'git")

    original_directory = os.getcwd()
    os.chdir(directory)

    if mode == 'scons':
        # If mode = scons, conduct a dry run to check whether 
        # all targets are up-to-date
        command = 'scons ' + directory + ' --dry-run'
    else:
        # If mode = git, check whether .sconsign.dblite has changed
        # since the last commit.
        original_directory = os.getcwd()
        os.chdir(directory)
        command = 'git status'
    
    logpath = '.temp_log_up_to_date'
    
    with open(logpath, 'wb') as temp_log:
        subprocess.call(command, stdout = temp_log, 
                        stderr = temp_log, shell = True)
    
    with open(logpath, 'rU') as temp_log:
        output = temp_log.readlines()
    os.remove(logpath)
    
    # Strip the output lines of white spaces.
    output = map(lambda s: s.strip(), output)

    if mode == 'scons':
        # First, determine whether the directory specified as a function
        # argument is actually a SCons directory.
        # We use the fact that running scons outside of SCons directory
        # produces the message: "No SConstruct file found."
        if [True for out in output if re.search('No SConstruct file found', out)]:
            raise ReleaseError('up_to_date(mode = scons) must be run on a '
                               'SCons directory.')
        # If mode = scons, look for a line stating that the directory is up to date.
        result = [True for out in output if re.search('is up to date\.$', out)]

    else:  
        # Determine whether the directory specified as a function
        # argument is actually a git repository.
        # We use the fact that running `git status` outside of a git directory
        # produces the message: "fatal: Not a git repository"
        if [True for out in output if re.search('Not a git repository', out)]:
            raise ReleaseError('up_to_date(mode = git) must be run on a '
                               'git repository.')

        # If mode = git, look for a line stating that sconsign.dblite has changed
        # since the latest commit.
        result = [out for out in output if re.search('sconsign\.dblite', out)]
        result = [True for out in result if re.search('modified', out)]
        result = not bool(result)

    os.chdir(original_directory)

    # Return the result.
    return bool(result)


def extract_dot_git(path = '.git'):
    '''
    Extract information from a GitHub repository from a
    .git directory

    This functions returns the repository, organisation, and 
    branch name of a cloned GitHub repository. The user may
    specify an alternative path to the .git directory through
    the optional `path` argument.
    '''
    # Read the config file in the repository's .git directory
    try:
        details = open('%s/config' % path, 'rU').readlines()
    except Exception as err:
        raise ReleaseError("Could not read %s/config. Reason: %s" % \
                           (path, str(err)))

    # Clean each line of this file's contents
    details = map(lambda s: s.strip(), details)
    
    # Search for the line specifying information for origin
    origin_line = [bool(re.search('\[remote "origin"\]', detail)) \
                   for detail in details]
    origin_line = origin_line.index(True)
    
    # The next line should contain the url for origin
    # If not, keep looking for the url line
    found_url = False
    for i in range(origin_line + 1, len(details)):
        url_line = details[i]
        if re.search('^url =', url_line):
            found_url = True
            break

    if not found_url:
        raise ReleaseError('url for git origin not found.')
    
    # Extract information from the url line
    # We expect one of:
    # SSH: "url = git@github.com:<organisation>/<repository>/.git"
    # HTTPS: "https://github.com/<organisation>/<repository>.git"
    repo_info   = re.findall('github.com[:/]([\w-]+)/([\w-]+)', url_line)
    organisation = repo_info[0][0]
    repo         = repo_info[0][1]

    # Next, find the branch's name
    branch_info = open('%s/HEAD' % path, 'rU').readlines()
    branch = re.findall('ref: refs/heads/(.+)\\n', branch_info[0])[0]

    return repo, organisation, branch
