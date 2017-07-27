## Notes on release.py

Make a release from an SCons directory by running the following
from the command line within the directory of interest:

```sh
python -m gslab_scons.release version=<version name here>
```
    
where `<version name here>` is the name of the version that
that will be released. As an example, to release version
v1.2.1 of a directory, navigate to the root of the directory and run:

```sh
python -m gslab_scons.release version=v1.2.1
```

An automatic location for release can be specified in `user-config.yaml` with 

```yaml
release_directory: <release location here>
```

For example, to automatically release to Dropbox set

```
release_directory: /Users/you/Dropbox/release
``` 

Including the option `no_zip` will prevent files
from being zipped before they are released to the specified location.  

This release procedure will warn you when a versioned file
is larger than 2MB and when the directory's versioned content
is larger than 500MB in total.  

Instead of entering the GitHub token as a password when using `release`,
you can store it in `user-config.yaml` as

```yaml
github_token: <your token here>
```
