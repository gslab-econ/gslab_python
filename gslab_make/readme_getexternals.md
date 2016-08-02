====================================================
Readme for get_externals.py & get_externals_github.py
====================================================

Description:
get_externals.py is a python module which interprets to the system a formatted text document listing 
desired files to be exported via svn or a system copy command. Unless otherwise noted, the usage for 
get_externals_github.py will follow that of get_externals.py.

Note that get_externals_github.py is only intended to download assets from releases. It can not download
the release source code or other assets not contained within a release.

Usage:

Within a python script such as make.py, after importing get_externals() function inside
get_externals.py module:

	get_externals('externals.txt')

"externals.txt" refers to a tab-delimited text file containing information on the files 
desired. The destination directory is specified by an optional second parameter which by 
default is "../external". The log file produced by get_externals is automatically added to 
an optional third parameter which is by default '../output/make.log'. 

The full syntax is:

    get_externals(externals_file [, externals_dir [, makelog [, quiet]]]):

If makelog is an empty string '', the default log file './get_externals.log' will be unchanged. 

For example, if we want './get_externals.log' to be added to '../log/make.log' before being deleted, 
and the destination directory to be './depend', the call is:

	get_externals('externals.txt', './depend', '../log/make.log')
    
The fourth argument, quiet, is by default False.  Setting this argument to True suppresses standard output
and errors from svn.  If we want to run the above example without displaying the svn output, the call is:

    get_externals('externals.txt, './depend', '../log/make.log', True)
or:
    get_externals('externals.txt, './depend', '../log/make.log', quiet = True)
    
Note that the externals_file argument is required, and the rest are optional. Each 
optional argument can be provided as a key word argument.    
	
Prerequisites for both get_externals.py and get_externals_github.py:
1.  Python 2.7 installed and defined as an environment variable. [Installation of 2.7.9 is recommended]	

Additional prerequisites for get_externals_github.py:
1.  The “requests” python module needs to be installed.
2.  A token, with the proper authority, for GitHub’s API must be created beforehand. [get_externals_github.py
will prompt the user to enter the token. In Linux environments, one can simply copy and paste. In Windows environments, it will have to be typed out.]


It should be noted that, when get_externals.py is called, the .py files in /private/ (described below)
will be compiled into .pyc compiled files (which Python then reads). These are placed in the 
./private/__pycache___ directory.

========================
Map of /py/ directory
========================

* get_externals.py
The get_externals.py script executes the code, but the modules housed in /py/private perform most
of the legwork. As can be seen by reading get_externals, the broad structure is as follows:
	
	1.  GitHub Externals Only: Prompt user for GitHub token to access GitHub’s API.
	2.  Apply/parse options and input the externals text file into a readable array.
	3.  Create an instance of a directive (SvnExport, GitHub, or Copy) depending on which is specified in
	    that specific line.
	4.  Check the line for errors.
	5.  Clean the line.
	6.  Issue the directive's command.
	
* `/private/directives`
This module houses most of the code. The parent class, SystemDirective, is defined first. This defines
properties that any instance of any specific system directive will have. At this point, 
GitHubDirective, SvnExportDirective, and CopyDirective are sub-classes of SystemDirective. It is in these subclass 
definitions that we build on SystemDirective methods, to tailor them to each subclass.

* `/private/preliminaries`
As well as starting logging and inputting the externals text file to a readable array, this parses, 
checks and applies any options before directives.py.

* `/private/exceptionclasses`
This defines the custom exception classes which are called upon during a run. When used, the script
provides the exception instance with an error message which is displayed and printed to the logfile.
Three subclasses of CustomError are defined, to better specify the type of exception encountered.

* `/private/messages`
This houses any error messages or notes which are either printed directly to the logfile, or printed
in an exception statement.

* `/private/metadata`
This houses any metadata called on during the run of get_externals. At present, it only houses
the svn command syntax, settings (default destination directory and logfile) and locals 
(used to replace %svn%, %svnbranch%, and %gslab_l% placemarkers).

===========================
externals.txt File Format:
============================

This file needs to rows of numbers or characters, delimited by either tabs or 4 spaces,one for each file to be exported via svn.
The proper format is: rev	dir	file	outdir	outfile	notes


Column descriptions:
---------------------
*  rev 
  *  Revision number of the file/directory. Must be in integer format. If left blank along with directory column, get_externals.py will read the last specified revision number. If copying from a shared drive rather than the repository, list revision number as COPY.
*  dir
  *  Directory of the file/directory requested. As described above, %xxx% placemarkers are substituted in from predefined values in metadata.py. If left blank along with revision column, get_externals.py will read the last specified directory. 
*  file 
  *  Name of the file requested. If entire directory is required, leave column as a single *. If a file name wildcard is required place single * within filename (i.e., test*.txt will call test1.txt, test2.txt, and any file of this form). get_externals.py will also attempt
			to screen out bad file names. Cannot be left blank.
*  outdir	
  *  Desired output directory of the exported file/directory. Typically of the form ./subdir/. If left blank, will be filled with the first level of the externals relative path. 
*  outfile 
  *  Desired output name of the exported file/directory. If left as double quotes, indicates that it should have the same name. Note that the contents of a directory call will be exported to the specified outdir, regardless of the outfile name. Adding a directory name that is different from the default """" will place this subdirectory within the outdir. So if you'd like a directory named /dir/ to be called the same name, place it in external/dir/ and leave outfile as """". If you'd like to rename it /outdir/, place it in external/ and leave outfile as 'outdir'. Additionally, get_externals has the capability to assign a prefix tag to a collection of files to be exported, either through a folder export, or wildcard call. In order to do so, write in the outfile column '[prefix]*', where the prefix [prefix] will be attached to each exported file. 
*  notes
  *  Optional column with notes on the export. get_externals.py ignores this, but logs it.


Example of externals.txt:
----------
```
rev	dir	file	outdir	outfile	notes
4908	%svn%/analysis/voting/output/text/	*	./text/	""""
4908	%svn%/analysis/voting/output/	tables.txt	.	""""	
		appendixtable.txt	.	""""	
2325	%svn%/analysis/voting/spreadsheets/	Ayers Daily List audit.xls	./spreadsheets/	""""	
		E&P - Ayers audit.xlsx	./spreadsheets/	""""	
2325	%svn%/analysis/voting/spreadsheets/	Duplicate readers analysis - independence model.xlsx	./spreadsheets/	""""	
4908	%svn%/analysis/voting/output/figures/	*	./figures/	prefix_*	
COPY	%gslab_l%\cverbeck\test\contents\	test*.txt	.	""""
```


Parsing external.txt file:
--------------------------
Both Copy and SvnExport directives perform single operations on both files (in all cases) and entire 
folders (so long as prefixes aren't applied to its' contents). If only a subset of a folder is selected
('*' in file is prefixed and/or suffixed) and/or we prefix a folders' contents (outfile contains '*'),
then the matching list is loaded as an attribute to the directive, and each item is operated on seperately.


#############################
# externals_github.txt File Format:
#############################
This file needs to rows of numbers or characters, delimited by either tabs or 4 spaces,one for each file to be exported via GitHub.
The proper format is: url	outdir	outfile	notes


Column descriptions:
---------------------
*  url  
  *  Desired download url for the file in a specific GitHub release. This can be found by going to the file on GitHub and right clicking on the desired file in a release. Then select “copy link address”. get_externals_github.py will then use this url to parse the exact download url needed. The url given should be the complete url.
*  outdir 
  *  Desired output directory of the exported file/directory. Typically of the form ./subdir/. If left blank, will be filled with the first level of the externals relative path. 
*  outfile 
  *  Desired output name of the exported file/directory. If left as double quotes, indicates that it should have the same name as the asset name in GitHub. 
*  notes 
  *  Optional column with notes on the export. get_externals_github.py ignores this, but logs it.


Example of externals_github.txt:
----------
```
url	outdir	outfile	notes	
https://github.com/TaddyLab/politext/releases/download/v0.1/politext.pdf	./	""""
https://github.com/TaddyLab/politext/releases/download/BrownTalk/politext_slides.pdf	./	""""
```


Commenting in externals[_github].txt:
-----------------------------
Although not entirely recommended (comments should be migrated to readme.txt), one can place 
comments in externals.txt by leading off a line with a #. Note, however, that a # anywhere else in 
a line will not be read as a comment.

Error Logging:
---------------
The program is designed to catch as many error as possible. The error_check() method of each class
checks key syntax requirements are satisfied. However, it doesn't check for all errrors.

Instead, if a line of externals.txt is illegal, the error will be caught before or as the final 
command is issued. An example of the former case is trying to issue the command
	
	string = 'fig_*2*.txt'
	one,two = string.split('\*')

i.e. trying to force three objects into two. The error message, and traceback to its' location, is 
then printed to the logfile. If a line fails at execution, the error is again printed to the logfile, 
as well as the raw input line from externals.txt. Instead of get_externals providing the user a 
detailed list of possible causes, the user should examine the raw input and correct so the desired
file is exported.
