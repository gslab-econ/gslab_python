# GSLAB_Gencat 0.0.1

## Overview

The gencat (General Concatenator) module defines an abstract class useful for preprocessing raw data containing a large number of text fils. The gencat class supplies methods to 
  *  Unzip all archives in a single directory
  *  Concatenate unzipped files in a subclass-specified order and rezip them in a single zip file 
  *  Save a |-delimited text file that maps concatenated files back to original inputs

## Inputs

Required inputs are 
  *  A path to an input directory
  *  A path to a temporary directory
  *  A path to an output directory

## Use

Each sublass of gencat must define a dictionary with keys as new filenames and values as tuples of unzipped files to be concatenated. It must also define the subgroups of the new filenames that should be zipped together. 

The `main` method provides a fast interface to the gencat methods in an order that produces clean output each run. Note that the main method begins by removing and reinitializing the temporary and output directories. 
