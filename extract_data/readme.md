#################################################################
#  Readme for extract_data.py
#
#		Created by: CJ Verbeck, January 2012
#  
#################################################################

Description:
extract_data.py is a python script which flexibly extracts data from all raw files within a 
directory, processes and/or filters their content, and saves them to another location.

Usage:
	python extract_data.py -r [rawdirectory] -o [outdirectory]

where the [rawdirectory] refers to the directory containing the raw files to be extracted, and 
[outdirectory] refers to the location of the extracted files. Each directory option should be in
the format expected by the operating system. The data extraction process will be different for 
each task, and hence the details of the extraction process will be determined by the main tools 
contained required by custom.py: Custom_globals(), Custom_prelims(), Custom_proc(), and 
Custom_wrapup(). The user should customize these functions for each extraction task. 
	
Prequisites:
(1) Python 3.x installed and defined as an environment variable.

It should be noted that, when extract_data.py is called, the .py files in /private/ (described 
below) will be compiled into .pyc compiled files (which Python then reads). These are placed in the 
./private/__pycache___ directory.

#############################
# Map of /py/ directory
#############################

* extract_data.py
The extract_data.py script executes the code, but the modules housed in /py/private perform most
of the legwork. As can be seen by reading extract_data, the broad structure is as follows:

	(1) Parse command-line options.
	(2) Define custom globals.
	(3) Execute custom preliminaries (e.g., creating output file).
	(4) Looping over each file in the raw folder and each line of each file, execute custom 
        processing of line (e.g., filter certain lines to save to final output).
	(5) Execute custom wrapup (e.g., closing output file).

* /private/preliminaries
Contains functions for logging, parsing options, and locating files which are general to any 
extraction. Also defines a class for lines of raw data which can be expanded. 
	
* /private/custom
Contains majority of functional code; note that extract_data.py doesn't work if this script is 
absent. Must include functions Custom_globals, Custom_prelims, Custom_proc, and Custom_wrapup,
whose general functionality is described above. The code currently versioned is an example on 
Nielsen purchase data which needs to be modified if it is to be applied to anything else. 
    Custom_globals: Returns a variable dictionary to be passed to subsequent processes.
    Custom_prelims: Opens output file(s) and executes any other actions required by data 
        extraction task prior to line-by-line extraction.
    Custom_proc:    Taking a line of raw data, this function defines the extraction process and 
        writes output to the output file. 
    Custom_wrapup:  Closes output file(s) and executes any other actions requires by data
        extraction task after line-by-line extraction.

* /private/exceptionclasses
This defines the custom exception classes which are called upon during a run. When used, the script
provides the exception instance with an error message which is displayed and printed to the logfile.
Three subclasses of CustomError are defined, to better specify the type of exception encountered.

#############################
# Sample data extraction
#############################

Since custom.py is required for any data extraction, the extract_data library currently versioned 
is specific to a sample data extraction of Nielsen Raw data originally stored in the shared drive  
\\gsball-b\Nielsen_Raw\, and now sampled in .\test\sampledata. The characteristics of input and
output files are listed here:

Sample raw data:
       00122327693320080301    1 1    1.33NN
       00122361002420081025    1 1   14.99NN
       00122361002420081206    1 1   14.99NN
       00122361469920080112    1 1    9.99NN
       
Fixed-width columns of interest:        
'MOVE_TDLINK': [1,7]
'UPC': [8,19]
'MOVE_WK_END': [20,27]
'MOVE_UNIT': [30,32]
'MOVE_PRICE': [37,42]

Desired characteristics: UPC is from product_module 7738, as defined in file 
\\\\gsball-b\\Nielsen_Raw\\RMS2006-2010\\products\\ITEMCHARVALS. 

Sample output data (csv):
MOVE_TDLINK,UPC,MOVE_WK_END,MOVE_UNIT,MOVE_PRICE
518,7410161120,20080105,1,1.89
518,7410161120,20080105,1,1.89
518,7410161120,20080112,3,1.89
518,7410161120,20080112,3,1.89

Note that the output data is a subset of all raw input as determined by ITEMCHARVALS, and hence 
the sample lines for the raw and output files above don't directly correspond. 

To execute this example, simply run make.bat (which calls ./test/test_extract_data.py), or 
write 'python py/extract_data.py -r .\test\sampledata\ -o .\test\' at the command line. 


The specific functions of each custom tool are below: 
    Custom_globals: Notably, selects which module to extract. Also defines location of 
        characteristics file, fixed-width values of interest, and final CSV sort order. 
    Custom_prelims: Opens output CSV file and adds variable names. Also uses product 
        characteristics file to create a dictionary of all product modules of interest.
    Custom_proc:    For each line of raw data, separates into fixed-width fields, check which 
        are in the product module dictionary, and write fields of interest to output CSV. 
    Custom_wrapup:  Closes output CSV file, and sorts CSV according to order specified in 
        Custom_globals. 
        
#############################
# Errors tested
#############################
- incorrect raw data folder
- omitted options
- omitted option switch ('-r')
- illegal binary (non-data) input file in raw directory

        

