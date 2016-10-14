# GSLAB_Gencat 0.0.2

## Overview

The gencat (General Concatenator) module defines an abstract class useful for preprocessing raw data containing a large number of text fils. The gencat class supplies methods to 
  *  Unzip all archives in a single directory
  *  Concatenate unzipped files in a subclass-specified order and rezip them according to specified subgroups
  *  Save a |-delimited text file that maps concatenated files back to original inputs

## Inputs

Required inputs are 
  *  A path to an input directory
  *  A path to a temporary directory
  *  A path to an output directory

## Use

Each sublass of gencat must define two dictionaries. One dictionary with keys as new filenames and values as tuples of unzipped files to be concatenated. Another dictionary with the keys being the name of the new zipped files and the values being the concatenated files that should be zipped in each zipped archive.

The `main` method provides a fast interface to the gencat methods in an order that produces clean output each run. Note that the main method begins by removing and reinitializing the temporary and output directories. 
