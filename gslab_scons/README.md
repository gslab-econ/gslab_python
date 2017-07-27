Notes on release.py
-------------------

Make a release from an SCons directory by running the following
from the command line within the directory of interest:

```sh
python -m gslab_scons.release version=<version name here>
```
    
where `<version name here>` is the name of the version that
the user wishes to release. As an example, to release version
v1.2.1 of a directory, one would run:

```sh
python -m gslab_scons.release version=v1.2.1
```
from the root of the directory. 

The location of the release can be specified in `user_config.yaml` with 

```yaml
release_directory: <YOUR_RELEASE_DIR_HERE>
```

For example, the user can automatically release it to their DropBox by setting `release_directory: /Users/you/Dropbox/release`. 

Including the option `no_zip` will prevent the release files
from being zipped before their release to a .

This release procedure will warn the user when a versioned file
is larger than 2MB and when the directory's versioned content
is larger than 500MB in total.  

Instead of entering the GitHub token as a password when using `release`,
the user can store it `user-config.yaml` in the relevant template as

```yaml
github_token: <YOUR_TOKEN_HERE>
```
