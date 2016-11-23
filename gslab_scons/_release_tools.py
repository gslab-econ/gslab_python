import requests
import getpass
import re
import json
import time
import os
import sys
import shutil
import subprocess


def release(vers, DriveReleaseFiles = '', local_release = '', org = '', 
            repo = '', target_commitish = ''):
    '''Publish a release

    Parameters
    ----------
    env: an SCons environment object
    vers: the version of the release
    DriveReleaseFiles a optional list of files to be included in a
        release to Google Drive.
    local_release: The path of the release directory on the user's computer.
    org: The GtHub organisaton hosting the repository specified by `repo`.
    repo: The name of the GitHub repository from which the user is making
        the release.
    '''
    token         = getpass.getpass("Enter a GitHub token and then press enter: ") 
    tag_name      = vers
    releases_path = 'https://%s:@api.github.com/repos/%s/%s/releases' % (token, org, repo)
    session       = requests.session()

    ## Create release
    payload = {'tag_name':         tag_name, 
               'target_commitish': target_commitish, 
               'name':             tag_name, 
               'body':             '', 
               'draft':            'FALSE', 
               'prerelease':       'FALSE'}
    json_dump = json.dumps(payload)
    json_dump = re.sub('"FALSE"', 'false', json_dump)
    session.post(releases_path, data = json_dump)

    ## Delay
    time.sleep(1)

    ## Get release ID
    json_releases  = session.get(releases_path)
    json_output    = json_releases.content
    json_split     = json_output.split(',')
    tag_name_index = json_split.index('"tag_name":"%s"' % tag_name)
    release_id     = json_split[tag_name_index - 1].split(':')[1]

    ## Get root directory name on Drive
    path = local_release.split('/')
    ind = 0
    i = 0
    while ind == 0:
        if re.search('release', path[i]):
            ind = 1
            i = i + 1
        else:
            i = i + 1
    dir_name = path[i]

    ## Release Drive
    if DriveReleaseFiles != '':
        
        # Install the DriveReleaseFiles in local_release
        if not os.path.isdir(local_release):
            os.makedirs(local_release)

        for path in DriveReleaseFiles:
            file = os.path.basename(path)
            shutil.copy(path, os.path.join(local_release, file))

        DrivePath = DriveReleaseFiles
        
        for i in range(len(DrivePath)):
            path = DrivePath[i]
            path = path.split('/')
            DrivePath[i] = 'release/%s/%s/%s' % (dir_name, vers, path[len(path) - 1])
        
        with open('gdrive_assets.txt', 'w') as f:
            f.write('\n'.join(['Google Drive:'] + DrivePath))
        
        upload_asset(token, org, repo, release_id, 'gdrive_assets.txt')
        os.remove('gdrive_assets.txt')


def upload_asset(token, org, repo, release_id, file_name, content_type = 'text/markdown'):
    session = requests.session()
    files = {'file' : open(file_name, 'rb')}
    header = {'Authorization':'token %s' % token, 'Content-Type': content_type}
    upload_path = 'https://uploads.github.com/repos/%s/%s/releases/%s/assets?name=%s' % \
                  (org, repo, release_id, file_name)

    r = session.post(upload_path, files = files, headers = header)
    return r.content


def up_to_date(directory = '.'):
    '''
    This functions whether the targets of a directory run using SCons 
    are up to date.
    '''
    # Preliminaries
    command = 'scons ' + directory + ' --dry-run'
    logpath = '.temp_log_up_to_date'
    
    # Conduct a scons dry run, keeping the output
    with open(logpath, 'wb') as temp_log:
        subprocess.call(command, stdout = temp_log, shell = True)
    with open(logpath, 'rU') as temp_log:
        scons_output = temp_log.readlines()
    os.remove(logpath)
    
    # Strip the output lines of white spaces.
    scons_output = map(lambda s: s.strip(), scons_output)
    # Determine if there is a line stating that the directory is up to date.
    result = [True for out in scons_output if re.search('is up to date\.$', out)]
    # Return the result.
    return bool(result)


def extract_dot_git(path = '.git'):
    '''
    Extract information from a GitHub repository from a
    .git directory

    This functions returns the repository, organisation, and 
    branch name of a cloned GitHub repository. The user may
    specify an alternative path to the .git directory through
    the option `path` argument.
    '''
    # Read the config file in the repository's .git directory
    with open('%s/config' % path, 'rU') as config:
        details = config.readlines()
    
    # Clean each line of this file's contents
    details = map(lambda s: s.strip(), details)
    
    # Search for the line specifying information for origin
    origin_line = [bool(re.search('\[remote "origin"\]', detail)) \
                   for detail in details]
    origin_line = origin_line.index(True)
    
    # The next line should contain the url for origin
    incr = 1
    url_line  = details[origin_line + incr]
    # If not, keep looking for the url line
    while not re.search('^url =', url_line) and origin_line + incr + 1 <= len(details):
        incr += 1
        url_line  = details[origin_line + increment]
    
    # Extract information from the url line
    repo_info   = re.findall('github.com/([\w-]+)/([\w-]+)', url_line)
    organisation = repo_info[0][0]
    repo         = repo_info[0][1]

    # Next, find the branch's name
    with open('%s/HEAD' % path, 'rU') as head:
        branch_info = head.readlines()
    branch = re.findall('ref: refs/heads/([\w-]+)', branch_info[0])[0]
    # If the branch is master, just use the repository name. 
    if branch == 'master':
        branch = repo
    # Otherwise, concatenate the repository and branch names with a hyphen.
    else:
        branch = "%s-%s" % (repo, branch)

    return repo, organisation, branch
