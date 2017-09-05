## Notes on release.py

Make a release from an SCons directory by running the module `release`. 

A user can either run the following from the command line within the directory of interest (e.g. `gslab-econ/template/paper_slides`) or write a Python script to call the module (see "Python wrapper" section below). If using the command line, run the following:

```sh
python -m gslab_scons.release version=<version name here> readme=<readme path here>
```
    
where `<version name here>` is the name of the version that 
will be released, and `<readme path>` is the path from the current directory
to the repository readme file (default to `./README.md`). As an example, to release version
v1.2.1 of a directory with the README file one level up, navigate to the root of the directory and run:

```sh
python -m gslab_scons.release version=v1.2.1 readme=../README.md
```

An automatic location for release can be specified in `config_user.yaml` with 

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
you can store it in `config_user.yaml` as

```yaml
github_token: <your token here>
```

## Provenance

Making a release using this tool will automatically call `make_provenance()` from the module `provenance`create a `provenance` file (for more details, please see our [RA manual](https://github.com/gslab-econ/ra-manual/wiki/Data-Storage)). 

While calling the `release` module from the command line, one can specify the `make_provenance()` argument by adding `detail_limit=<###>` (default to 500).

## Python wrapper

If you wish to wrap the `release` module in a Python script to pass arguments to `make_provenance()`, use the following syntax:

```python
from gslab_scons import release
release.main(version = 'test_sep4',
             readme  = '../readme.md')
```

For a complete list of arguments that you can pass to `release.main()` and `make_provenance()`, visit `release.py` and `provenance.py` respectively. 