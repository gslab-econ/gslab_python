====================================
README FOR FUNCTIONS USED BY MAKE.PY
====================================

Description:
make.py is a python script which facilitates running programs in batch mode. It uses functions
in this directory to provide efficient and easy-to-understand commands, which are 
portable across different Unix/Windows systems.

Prerequisites:
*  Python 2.7 installed and executable path is added to system path
*  Matlab installed and and executable path is added to system path
*  Stata installed and executable defined as an environment variable / symbolic link
*  Perl installed and executable path is added to system path
*  Mathematica 8.0 installed and math kernel path is added to system path
*  StatTransfer installed and executable path is added to system path
*  Lyx installed and executable path is added to system path
*  R installed and executable path is added to system path
*  SAS installed and executable path is added to system path
*  Requires SVN Version 1.7 or higher. See ‘clear_dirs’ command below for reasoning.

==============================
List of functions for make.py
==============================


Optional parameters are in []

Default parameters are defined in /private/metadata -> settings
```
settings = {
    'external_dir'      : '../external/',
    'links_dir'         : '../external_links/',
    'externalslog_file' : './get_externals.log',
    'linkslog_file'     : './make_links.log',
    'output_dir'        : '../output/',
    'output_local_dir'  : '../output_local/',
    'temp_dir'          : '../temp/',
    'makelog_file'      : '../output/make.log',
    'manifest_file'     : '../output/data_file_manifest.log',
    'link_logs_dir'     : '../log/',
    'link_stats_file'   : 'link_stats.log',
    'link_heads_file'   : 'link_heads.log',
    'link_orig_file'    : 'link_orig.log',
    'stats_file'        : 'stats.log',
    'heads_file'        : 'heads.log'
}
```

Default options for Stata and Matlab are defined in /private/metadata -> default_options
```
default_options = {
    'rmdirwin'  : '/s /q',
    'rmdirunix' : '-rf',
    'matlab'    : '-nosplash -minimize -wait',
    'statawin'  : '/e',
    'stataunix' : '-b',
    'rbatch'    : '--no-save',
    'rinstall'  : '--no-multiarch',	
    'saswin'    : '-nosplash',
    'math'      : '-noprompt'
}
```

Default executables for each type of program are defined in /private/metadata -> default_executables
```
default_executables = {
    'statawin'      : '%STATAEXE%',
    'stataunix'     : 'statamp',
    'matlab'        : 'matlab',
    'perl'          : 'perl',
    'python'        : 'python',
    'math'          : 'math',
    'st'            : 'st',
    'lyx'           : 'lyx',
    'rbatch'        : 'R CMD BATCH',
    'rinstall'      : 'R CMD INSTALL',
    'sas'           : 'sas'
}
```

The file extensions for each program are defined in /private/metadata -> extensions
```
extensions = {
    'stata'         : '.do',
    'matlab'        : '.m',
    'perl'          : '.pl',
    'python'        : '.py',
    'math'          : '.m',
    'stc'           : '.stc',
    'stcmd'         : '.stcmd',
    'lyx'           : '.lyx',
    'rbatch'        : '.R',
    'rinstall'      : '',
    'sas'           : '.sas',
    'other'         : ''
}
```

--------------------
Module dir_mod.py
--------------------
Directory modification functions

* delete_all_files(top[, exceptfile])
  *  Delete every non-hidden file [except for any file with the same base name 
     as "exceptfile"] in non-hidden sub-directories reachable from the directory named 
     in "top". The original directory structure is kept intact (i.e. sub-directories are unchanged)
    
  *  CAUTION:  This is dangerous!  For example, if top == '/', it
     could delete all your disk files.

* delete_files(pathname)
  *  Delete a possibly-empty list of files whose names match "pathname", which must be a string 
     containing a path specification. "pathname" can be either absolute 
     (like /usr/src/Python-1.5/Makefile) or relative (like ../../Tools/*/*.gif), 
     and can contain shell-style wildcards.

* list_directory(top[, makelog])
  *  List all non-hidden sub-directories of "top" and their content from top down. 
     Write their names, modified times and sizes in bytes to "makelog" log file

* check_manifest([manifestlog[, output_dir[, makelog]]]
  *  Produce an error if there are any .dta files in "output_dir" and all non-hidden sub-directories
     that are not in the manifest file "manifestlog", and produce a warning if there are .txt 
     or .csv files not in the manifest along with a list of these files. All messages are printed
     to "makelog" log file.

* remove_dir(pathname, [options])
  *  Completely remove a directory using the 'rmdir' command in Windows or 'rm' command in Linux
     (useful for removing symlinks without deleting the source files or directory.)

* clear_dirs(*args):
  *  Use remove_dir() to remove each arg in *args and then
     recreates the directory for each arg in *args if they do not already exist. Safe for symlinks.
    
--------------------    
Module make_log.py
--------------------
Function to set default options
Functions to start and end make.log
Functions to add to and delete from make.log

Note that start_make_logging must be called before end_make_logging, add_log, 
or del_log may be called.

* set_option(**kwargs)
  *  This function takes a dictionary as the input and overwrite the default values of 
     the settings in metadata. The key identifies the setting to be changed, and the value 
     will be the new default value of that setting.
    
  *  The keys should match with the ones identified by metadata.setting (see above).
     For the keys that end with "_file", "_file" can be omitted. If both syntaxes are used an error 
     will be raised.
     For the keys that end with "_dir", "_dir" can be omitted. If both syntaxes are used an error 
     will be raised.

* start_make_logging([makelog])
  *  Start "makelog" log file with time stamp and current directory information.

* end_make_logging([makelog])
  *  End "makelog" log file with time stamp.

* add_log(*args, **kwargs)
  *  Add log files in "*arg" to default makelog file.
     Or, add log files to user-defined makelog file 
     by assigning variable 'makelog' in kwargs.
    
* del_log(*args, **kwargs)
  *  Delete each of the log files listed in "*arg".
     Errors are printed to default makelog file or 
     printed to user-defined makelog file by 
     assigning variable makelog in kwargs.
    
* make_output_local_logs([output_local_dir [, output_dir [, stats_file [, heads_file [, recur_lim]]]]])
  *  Creates stats_file and heads_file for the files in "output_local_dir" up to a 
     directory depth of "recur_lim". (Calls make_stats_log and make_heads_log)
    
  *  If `stats_file == ''` no stats_file is created.
  *  If `heads_file == ''` no heads_file is created.
  *  If `recur_lim == 0 (or false)` ther is no depth limit.
    
* make_stats_log(output_dir, stats_file, all_files)
  *  Create a log of summary statistics of all files in "all_files".
     The summary statistics are time last modified and file size.
     Append to existing results if "stats_file" already exists.
    
* make_heads_log(output_dir, heads_file, all_files, head_lines)
  *  Create a log of the first "head_lines" of all the files in "all_files".
     Append to existing results if "heads_file" already exists.
    
--------------------
Module run_program.py
--------------------   
Functions to run:    
Stata, Matlab, Perl, Python, StatTransfer, Mathematica, Lyx, R

```
run_stata(**kwargs)
run_matlab(**kwargs)
run_perl(**kwargs)
run_python(**kwargs)
run_mathematica(**kwargs)
run_stc(**kwargs)
run_stcmd(**kwargs)
run_lyx(**kwargs)
run_rbatch(**kwargs)
run_rinstall(**kwargs)
run_sas(**kwargs)
run_command(**kwargs)
```

These functions use the RunProgramDirective class defined in /private/runprogamdirective.py.

**kwargs format :
Note: This is a dictionary, thus the order of the parameters does not matter and 
parameters can be omitted unless specified otherwise.
(a list of keyname = value separated by commas)

```
program = string_program            (required, except for run_rinstall and run_command)
package = string_package            (required, only for run_rinstall)
command = string_command            (required, only for run_command)
makelog = string_makelog            (optional, default = '../output/make.log')
option = string_option              (optional, not for run_command)
lib = string_lib                    (optional, only for run_rinstall)
log = string_log                    (optional, default = '')
lst = string_lst                    (optional, default = '../output/', only for run_sas)
changedir = bool_changedir          (optional, default = False, not for run_matlab, run_rinstall or run_command)
executable = string_executable      (optional, not for run_command)
args = string_arg                   (optional, only for run_perl and run_python)
pdfout = string_pdfout              (optional, only for run_lyx)
handout = bool_handout              (optional, only for run_lyx)
comments = bool_comments            (optional, only for run_lyx)
```

* [string_program] is a string that specifies the file path of program to be run. 

  *  If this parameter is not specified a critical error message will be raised.

* [string_package] is a string that specifies the list of packages (path included) 
to be installed by run_rinstall.

* [string_command] is a string that specifies the Shell command to be run. This option is used
only with run_command(). 

* [string_lib] is a string that specifies the path name of the R library tree to install to.


* [string_makelog] is a string that specifies the path name of the main log file (usually make.log).
  *  This can be specified when the desired make.log is not the same as the default one
     (different name and/or location).

  *  If makelog == '', the output from the run will not be logged in the main makelog file (to specify a
     file into which output can be saved, define [string_log]).

* [string_option] is a string to specify running options.

* [string_log] specifies the path name of the log file that the output content is to be stored as. 

```
if [string_makelog] != ''
    [string_log] == '' (default): 
        Add output content to the main log file (make.log) without saving it as an independent log file.
    [string_log] == log file path: 
        Output content is saved as [string_log] and also added to the main log file (make.log).
```

```
if [string_makelog] == ''
    [string_log] == '' (default): 
        No output will be saved.
    [string_log] == log file path: 
        Output content is saved as [string_log].   
```        


  *  Alternatively, use add_log() and del_log() described above to work with log files. This will allow 
     behaviors that are not specified by the default above.

* [string_lst] specifies the path name of the lst file that will be stored by run_sas.

  *  [string_lst] == '../output/' (default):
     Save output to output folder and save contents into the main log file (make.log).
  *  [string_lst] == lst file path:
     Save output to lst file path and save contents into the main log file (make.log).

* [bool_changedir] is a Boolean (True/False) value if we need to change directory to run the program

  *  [bool_changedir] = True: if the program specified by [string_program] is not in the 
     current directory, then run_program will first change directory to the directory which holds program, 
     execute, then return to the current directory after the program completes. This is the default
     behavior for run_matlab (Matlab only allows a local script to be run) but not the default 
     for other programs.

  *  [bool_changedir] = False (default, except for run_matlab): run_program executes the program 
     specified by [string_program] inside the current directory.

* [string_executable] is a string to specify the executable to run the program if not the default.
  *  If the program environment variable is not set up as defined in default_executables (see above),
     use this option to specify it instead.

* [string_args] is a string to specify the arguments in a Perl or a Python programs that 
require them.

* [string_pdfout] is a string to specify the location of the pdf output when compiling a lyx file 
using run_lyx(). If unspecified, run_lyx('file.lyx') produces 'file.pdf' in the output directory.

* [bool_handout] is a Boolean (True/False) value to specify if we want a handout version of the pdf output 
when compiling a lyx file using run_lyx().

  *  [bool_handout] = True: if the document class is beamer, the 'handout' option of the beamer class is turned on, 
     and there will be no pauses in output slides. By default, the handout version of the pdf output with '_handout' 
     appended to the name is produced in the temp directory unless [string_pdfout] is used to specify the location of the pdf output. 

* [bool_comments] is a Boolean (True/False) value to specify if we want to print out the lyx notes when compiling a lyx file using run_lyx().

  *  [bool_comments] = True: converts all the lyx notes to 'Greyed out' notes for them to be visible in pdf output.
     By default, the commented version of the pdf output with '_comments' appended to the name is produced in the
temp directory unless 
      - [bool_handout] = True in which case '_handout' is appended to the name instead.
      - [string_pdfout] is used to specify the location of the pdf output. 


====================================
Examples of functions for make.py
====================================


See Templates (/svn/admin/Templates) for Examples

Additional examples:

--------------------
Module dir_mod.py
--------------------

* delete_files

- To delete all pdf files in the current folder:
    `delete_files('./*.pdf')`

    
* list_directory

- To list all non-hidden files in ../output and its non-hidden sub-directories to the default
make.log (../output/make.log)
    `list_directory('../output')`

- To list all non-hidden files in ../output and its non-hidden sub-directories to logfile.txt
    `list_directory('../output', 'logfile.txt')`

- An example of what the output will look like:
        
List of all files in sub-directories in ../output
```
../output
created/modified Wed Jun 06 18:00:51 2012
                                    helloworld.log --- created/modified Wed Jun 06 15:25:26 2012 ( 31 bytes  )
                                          make.log --- created/modified Wed Jun 06 18:03:19 2012 ( 14,847 bytes )
                                       results.log --- created/modified Wed Jun 06 15:25:17 2012 ( 71 bytes )
../output\dta
created/modified Wed Jun 06 18:00:05 2012
                                      adPrices.dta --- created/modified Wed Jun 06 15:44:45 2012 ( 9,685,444 bytes )
                                         adVol.dta --- created/modified Wed Jun 06 15:45:18 2012 ( 10,153,730 bytes )
```                                         

                                         
* check_manifest

- To check if .dta files in ../output and all of its non-hidden sub-directories are listed
in ../output/manifest.log:
    `check_manifest('../output', '../output/manifest.log')`
    
  *  File paths in the manifest log file should start with "File: ", and if there is no file extension
     then ".dta" is the default.
    
  *  Note that .txt and .csv files are checked as well, but only warnings will be issued.

* remove_dir

- To remove a directory using command line arguments rather than Python functions:
    `remove_dir('../to_remove/')`

- This is useful for removing symlinks because some versions of Python remove both the source and
link files when the 'os.remove' function is used, so the command line is necessary.

    *  Note: In all of the above examples, the default output directory, manifest file, make log file
       can be specified once using set_option() in make_log module.

* clear_dirs

  - This is usually put at the start of make.py before start_make_logging() and before get_externals(). Every folder
  that output, temporary files, or external file are to be placed in must be explicitly called. If the folder does not already
  exist, then it will be created. Note that this function should be used for local directories also. A standard example can be found below:
  ```
    clear_dirs('../output/', '../temp/', '../external/')
    start_make_logging()
  ```

Note that since this command deletes the entire directory any version control metadata will be deleted also. This is fine for SVN versions 1.7 or higher, as the metadata is stored in the root of the working copy instead of in each individual folder.
   
--------------------    
Module make_log.py
--------------------
* set_option

- This function can be used to overwrite the default setting options [** clear_dirs() has no defaults and thus, is not affected 
by set options **]. All other functions that come after it will not have to re-specify those options. For example:
```
    set_option(makelog = 'make.log', temp_dir = '', output_dir = './log', 
               external_dir = './external', manifest = './manifest.log', 
               externalslog = './log/externals.log')
```
                
  -  Each of the above is optional. For all keys, "_dir" and "_file" are optional.


* start_make_logging

  -  This is usually put at the start of make.py. To start the default '../output/make.log' 
     with time stamp:
    `start_make_logging()`
    
  - If we want to store the log file in './make.log' instead:
    `start_make_logging('make.log', '', '')`

    
* end_make_logging

  - To end make.py by putting the time stamp in the default '../output/make.log':
    `end_make_logging()`

  - If the log file is different, we have to specify it:
    `end_make_logging('logfile.txt')`


* add_log

  -  If there are log files created inside the programs (for example from a Perl or Python program), and 
we want to append their content to the end of the default log file (usually '../output/make.log'):

    `add_log('../output/analysis.log', '../output/another_log.log')`
    
  *  The number of log arguments can vary. If the log files don't actually exist, errors will be 
     printed to the common log file.

  -  If we want to append content of log files to a different log file than the default:

     `add_log('../output/analysis.log', '../output/another_log.log', makelog = '../different.log')`

* del_log

  - After we append the various log files to the common one using add_log, we may want to delete
    the extra ones to clean up the output folder. Here is the command:

    `del_log('../output/analysis.log', '../output/another_log.log')

  *  If variable 'makelog' is not defined in kwargs, errors from del_log will be printed to the
     default makelog (usually '../output/make.log'). If we want to specify a different log to which
     we print the errors:

    `del_log('../output/analysis.log', '../output/another_log.log', makelog = '../different.log')`


* make_output_local_logs

  -  In svn_derived_local directories, the output_local directory is not committed to the
     repository, but it still contains important output. make_output_local_logs is called
    after the output_local content has been created to log the most important features.
  
  -  Normally, the call can just be make_output_local_logs(), but to choose values other
     than the defaults:
  
 ``` 
    make_output_local_logs(output_local_dir = '../other_output_local/', 
                           output_dir = '../output_logs_dir/', 
                           stats_file = 'other_stats.log', 
                           heads_file = 'other_heads.log',
                           recur_lim = False)
```                           
                           
    *  This will log all the files in '../other_output_local/' and all its subdirectories
       (there is no depth limit because recur_lim == False). The logs would be named 
       'other_stats.log' and 'other_heads.log' and would be saved in '../output_logs_dir/'.
  
* make_stats_log

  -  This is called by make_output_local_logs, and will not normally be called independently.

* make_heads_log

  -  This is called by make_output_local_logs, and will not normally be called independently.

  *  Note: In all of the above functions, the default for output directory, temp directory, 
     make log file can be specified once using set_option().

    
--------------------
Module run_program.py
--------------------   

* run_matlab

  -  To run 'analysis.m' if the common log file is the default one '../output/make.log':
    
   `run_matlab(program = 'analysis')`
or
    `run_matlab(program = 'analysis.m')`  
    
  -  This will execute and process the log file:
    `matlab -r analysis -logfile analysis.log -nosplash -minimize -wait`
    
  -  Note that analysis.log will be added to '../output/make.log' and then deleted. The default
     option is '-nosplash -minimize -wait', which can be changed by specifying option = '' as 
     an additional argument.
   
  - To run './sub/analysis.m' by stepping into the './sub' folder before executing the .m file,
    given that the common log file is '../log/make.log':

    `run_matlab(program = './sub/analysis.m', changedir = True, makelog = '../log/make.log')`
    
  -  In fact, for run_matlab, the changedir option is always True because the Matlab call
     executes a command, and is not a call to a Matlab file.

  - To run 'analysis.m' if the common log file is '../log/make.log' and we do not want to 
    delete the default 'analysis.log' but save it as '../log/program.log':

    `run_matlab(program = 'analysis', makelog = '../log/make.log', log = '../log/program.log')`
    
  -  The default log produced by the call is still added to make.log but it remains an
     independent file program.log in ../log as well.

  -  Note that option = '-logfile ../log/program.log' and log = '../log/program.log' will be treated
     equivalently (both will use log = '../log/program.log'). The "log =" method is preferred over the
     "option =" method.

  -  Furthermore, if both option = '-logfile ../log/program.log' and log = '../log/program.log' are
     defined as in:

    `run_matlab(program = 'analysis', log = '../log/program.log', option = '-logfile ../log/program.log')`

    this will throw an error. Choose only one of these options (preferably "log = ").


* run_stata

  *  See the above example for run_matlab, with 'analysis.m' replaced by 'analysis.do'. 
    
  *  This will execute and process the log file:

    ```
    Windows: %%STATAEXE%% /e do analysis.do
    Unix:    statamp -b do analysis.do
    ```

    
  *  To run analysis.do with StataSE as the executable instead:    
    `run_stata(program = 'analysis.do', executable = 'stataSE');`
    

* run_perl

  -  To run 'perl_program.pl' if the common log file is the default one '../output/make.log', 
     and we want to add output content to make.log and as an independent log file 
     '../output/perl_program.log':
    
    `run_perl(program = 'perl_program', log = '../output/perl_program.log')`

  -  To run 'external/lib/perl/tablefill/tablefill.pl' given that the argument is 
     '-i external/tables.txt -t tables.lyx -o tables_filled.lyx', and we do not want to change
     directory when executing this program

    ```
    run_perl(program = 'external/lib/perl/tablefill/tablefill.pl', args = '-i external/tables.txt -t tables.lyx -o tables_filled.lyx')
    ```
    
  -  Note that the changedir = False is optional because this is the default. This is equivalent to executing:
     perl external/lib/perl/tablefill/tablefill.pl -i external/tables.txt -t tables.lyx -o tables_filled.lyx
    

* run_python

See the above example for run_perl


* run_mathematica

 -  To run 'graph.m' with the default common log file '../output/make.log':
    
    ```run_mathematica(program = 'graph.m')```

 -  This will execute and process the log file:
    math -script graph.m
    
    
* run_lyx
        
  -  To create pdf file for 'draft.lyx' with the log file being './make.log':
    
    `run_lyx(program = 'draft', makelog = './make.log')`

  -  This will execute and process the log file:
     lyx -e pdf2 draft.lyx
    
  -  By default, the pdf file is saved in the output directory, and has the same name as the lyx file.
     e.g. if `set_option(output_dir = '../output')`,
     then `run_lyx(program = 'draft') produces '../output/draft.pdf'`.

  -  The name and location of the output pdf file can be specified using the 'pdfout' argument'.
     e.g. `run_lyx(program = 'draft' pdfout = '../temp/file.pdf') produces '../temp/file.pdf'`.
    
    
* run_rbatch

  -  To run 'runtopics.R' with the default common log file '../output/make.log':
     `run_rbatch(program = 'runtopics.R')`

  -  This will execute and process the log file:
     R CMD BATCH --vanilla runtopics.R runtopics.Rout

  -  The default option is '--vanilla' which can be changed by setting option = '', the default
     log runtopics.Rout is then added to the common log file and deleted. If we want to keep the
     log file, specify the desirable file path with log = [file_path] option.


* run_rinstall

  - To install R packages '../external/textir/textir_1.8-6.tar.gz' to library folder '../temp' with 
    option '--no-multiarch':
    `run_rinstall(package = '../external/textir/textir_1.8-6.tar.gz', lib = '../temp', option = '--no-multiarch')`

  -  This will execute and process the log file:
     R CMD INSTALL --no-multiarch -l ../temp ../external/textir/textir_1.8-6.tar.gz

    
* run_stc

  -  To run StatTransfer batch program with .stc extension 'convert.stc' and the common log
     file is saved in string variable makelog_file:
    
    `run_stc(program = 'convert', makelog = makelog_file)`
    
  -  This will execute and process the log file:
     ST convert.stc

    
* run_stcmd    

  -  To run StatTransfer batch program with .stcmd extension 'convert.stcmd' and the common log
     file is saved in string variable makelog_file:
    
    `run_stcmd(program = 'convert', makelog = makelog_file)`
    
  -  This will execute and process the log file:
     ST convert.stcmd

* run_sas

  -  To run 'stats.sas' with the default common log file '../output/make.log':
    
    `run_sas(program = 'stats')`

  -  This will execute and process the log file:
  ```
    Windows: sas stats.sas -nosplash
    Unix:    sas stats.sas
  ```  

  -  Note that `option = '-log ../log/program.log' and log = '../log/program.log'` will be treated
     equivalently (both will use log = '../log/program.log'). The "log =" method is preferred over the
     "option =" method.

  -  Furthermore, if both option = '-log ../log/program.log' and log = '../log/program.log' are
     defined as in:

    `run_sas(program = 'analysis', log = '../log/program.log', option = '-log ../log/program.log')`

     this will throw an error. Choose only one of these options (preferably "log = ").

  -  The previous two notes also hold for `option = '-print ../lst/program.lst'` and
     `lst = '../lst/program.lst'`. Using "lst =" is the preferred method.

* run_command

  -  This function is to faciliate any other Shell command that has not yet been implemented as a 
     stand-alone function. To run the command 'wzzip -a -P -r ../output/gentzkow_shapiro_data.zip ./*.*',
     with main log file 'make.log' and log file 'zip.log':

    `run_command(command = 'wzzip -a -P -r ../output/gentzkow_shapiro_data.zip ./*.*', makelog = 'make.log', log = 'zip.log')`
    
* Note: In all of the above examples, _makelog_ option can be specified once by using
  set_option() in make_log module. 