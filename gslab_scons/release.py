import requests
import getpass
import re
import json
import time
import os
import sys
import shutil
from _exception_classes import ReleaseOptionsError

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


if __name__ == '__main__':
    # Make a release

    # Read the config file in the repository's .git directory
    with open('.git/config', 'rU') as config:
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
    with open('.git/HEAD', 'rU') as head:
        branch_info = head.readlines()
    branch = re.findall('ref: refs/heads/([\w-]+)', branch_info[0])[0]
    # If the branch is master, just use the repository name. 
    if branch == 'master':
        branch = repo
    # Otherwise, concatenate the repository and branch names with a hyphen.
    else:
        branch = "%s-%s" % (repo, branch)

    # Determine the version number
    try:
        version = next(arg for arg in sys.argv if re.search("^version=", arg))
    except:
        raise ReleaseOptionsError('No version specified.')

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
