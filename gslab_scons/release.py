import requests
import getpass
import re
import json
import time
import os
from _exception_classes import ReleaseOptionsError

def release(env, vers, DriveReleaseFiles = '', local_release = '', org = '', 
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
        env.Install(local_release, DriveReleaseFiles)
        env.Alias('drive', local_release)
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

    # i) Read options from file in root of repository

    # Example user_options.txt
    #------------------------------------------------------
    # name: template
    # organization: gslab-econ
    # release files: "test.txt", "other_test.rds"
    #
    #------------------------------------------------------

    if not os.path.exists('user_options.txt'):
        raise ReleaseOptionsError('No user_options.txt file found.')

    with open('user_options.txt', 'rU') as options_file:
        user_options = options_file.readlines()

    # ii) Process the options into a dictionary
    user_options = map(lambda s: s.split(': '), user_options)
    options_dict = dict()
    
    for option in user_options:
        options_dict[option[0]] = option[1].strip()

    for required_field in ['name', 'organization', 'release files']:
        if required_field not in options_dict.keys():
            raise ReleaseOptionsError(required_field + ' missing from user_options.txt.')

    
    options_dict['release files'] = options_dict['release files'].split(',')
    options_dict['release files'] = map(lambda s: re.sub('[\s]?\'', '', s), 
                                      options_dict['release files'])

    # iii) Determine the version number
    try:
        version = next(arg for arg in sys.argv if re.search("^version=", arg))
    except:
        raise ReleaseOptionsError('No version specified.')

    version = re.sub('^version=', '', version)

    # iv) Install files in their appropriate locations
    USER = os.environ['USER']
    local_release = '/Users/%s/Google Drive/release/%s/' % (USER. options_dict['name'])
    local_release = local_release + version + '/'

    release(env, version, 
            DriveReleaseFiles = options_dict['release files'], 
            local_release     = local_release, 
            org               = options_dict['organisation'], 
            repo              = options_dict['name'])
