GSLab Python Library Collection 1.1.1
=====================================

Overview
--------
This repository contains the following GSLab Python libraries:
 - gslab_make
 - gslab_fill  
 - gslab_scons
 - gencat

Information about each of these packages is available in its internal documentation. 

Installation
------------
To install this repository's Python libraries, run the `setup.py` script at its root
with the command:
```
python setup.py install [clean]
```
where the optional clean command deletes files used in installating the libraries
after installation is complete.

One can use `pip` to assist with this installation procedure by using the commands:
```
pip install git+ssh://git@github.com/gslab-econ/gslab_python.git
```
or
```
pip install git+https://git@github.com/gslab-econ/gslab_python.git
```
noting that the SSH command requires a working GitHub SSH keypair and that, when
the user has enabled two-factor authentication, the HTTPS command requires the user
to have a working GitHub personal access token. 
