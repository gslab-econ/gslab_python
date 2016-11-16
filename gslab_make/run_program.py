#! /usr/bin/env python
'''
These functions use the RunProgramDirective class defined in /private/runprogamdirective.py.

**kwargs format :
Note: **kwargs is a dictionary, thus the order of the parameters does not matter and 
parameters can be omitted unless specified otherwise.
(a list of keyname = value separated by commas)

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

Keyword argument descriptions
-----------------------------
* [string_program] is a string that specifies the file path of program to be run. 

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

    if [string_makelog] != ''
        [string_log] == '' (default): 
            Add output content to the main log file (make.log) without saving it as an independent log file.
        [string_log] == log file path: 
            Output content is saved as [string_log] and also added to the main log file (make.log).

    if [string_makelog] == ''
        [string_log] == '' (default): 
            No output will be saved.
        [string_log] == log file path: 
            Output content is saved as [string_log].   

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
  *  [bool_handout] = True: if the document class is beamer, the 'handout' option of the beamer class 
        is turned on, and there will be no pauses in output slides. By default, the handout version of
        the pdf output with '_handout' appended to the name is produced in the temp directory unless 
        [string_pdfout] is used to specify the location of the pdf output. 

* [bool_comments] is a Boolean (True/False) value to specify if we want to print out the lyx notes when 
    compiling a lyx file using run_lyx().
  *  [bool_comments] = True: converts all the lyx notes to 'Greyed out' notes for them to be visible in pdf output.
     By default, the commented version of the pdf output with '_comments' appended to the name is produced in the
     temp directory unless 
      - [bool_handout] = True in which case '_handout' is appended to the name instead.
      - [string_pdfout] is used to specify the location of the pdf output. 
'''

import os
import shutil
import fileinput

import private.metadata as metadata
import private.messages as messages
from private.exceptionclasses import SyntaxError
from private.runprogramdirective import (RunProgramDirective, 
                                         RunCommandDirective, 
                                         RunRPackageDirective)
from private.preliminaries import add_error_to_log


def run_stata(**kwargs):
    """Execute a Stata script 

    Description:
    This function executes a Stata script and produces a log file
    for this run.

    e.g. To run the script analysis.do with the default specifications,
         use the command:
        `run_stata(program = 'analysis.do')` or 
        `run_stata(program = 'analysis')` 

        To run analysis.do with StataSE as the executable instead:    
        `run_stata(program = 'analysis.do', executable = 'stataSE');`
    """

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('stata')

        # Set option
        option = run.option
        if not option:
            if run.osname == 'posix':
                option = metadata.default_options['stataunix']
            else:
                option = metadata.default_options['statawin']

        # Set executable
        executable = run.executable
        if not executable:
            if run.osname == 'posix':
                executable = metadata.default_executables['stataunix']
            else:
                executable = metadata.default_executables['statawin']

        # Set default_log
        if run.changedir:
            program = '"' + run.program + '"'
            default_log = os.path.join(run.program_path, run.program_name + '.log')
        else:
            program = '"' + os.path.join(run.program_path, run.program) + '"'
            default_log = os.path.join(os.getcwd(), run.program_name + '.log')

        command = metadata.commands['stata'] % (executable, option, program)
        run.execute_run(command)

        run.move_log(default_log)
    except:
        add_error_to_log(run.makelog)


def run_matlab(**kwargs):
    """ Run a Matlab script

    Description:
    This function executes a Matlab script and produces a log file
    for this run. See private/metadata.py for its defaults.

    e.g. To run the script analysis.do with the default specifications,
         use the command:
        `run_matlab(program = 'analysis.m')` or 
        `run_matlab(program = 'analysis')` 
    """

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('matlab')
        run.changedir = True

        # Get option
        option = run.option
        if not run.option:
            if run.osname == 'posix':
                option = metadata.default_options['matlabunix']
            else:
                option = metadata.default_options['matlabwin']
        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['matlab']

        program = run.program_name
        default_log = os.path.join(run.program_path, run.program_name + '.log')
        command = metadata.commands['matlab'] % (executable, program, run.program_name + '.log', option)

        run.execute_run(command)
        run.move_log(default_log)
    except:
        add_error_to_log(run.makelog)


def run_perl(**kwargs):
    """Execute a Perl script"""

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('perl')
        if run.changedir:
            program = '"' + run.program + '"'
        else:
            program = '"' + run.program_full + '"'

        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['perl']

        command = metadata.commands['perl'] % (executable, run.option, program, run.args)

        run.execute_run(command)
    except:
        add_error_to_log(run.makelog)


def run_python(**kwargs):
    """Execute a Python script."""

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('python')
        if run.changedir:
            program = '"' + run.program + '"'
        else:
            program = '"' + run.program_full + '"'

        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['python']

        command = metadata.commands['python'] % (executable, run.option, program, run.args)

        run.execute_run(command)
    except:
        add_error_to_log(run.makelog)


def run_mathematica(**kwargs):
    """Execute a Mathematica script"""

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('math')
        if run.changedir:
            program = '"' + run.program + '"'
        else:
            program = '"' + run.program_full + '"'
        # Get option
        option = run.option
        if not run.option:
            option = metadata.default_options['math']

        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['math']

        command = metadata.commands['math'] % (executable, program, option)

        run.execute_run(command)
    except:
        add_error_to_log(run.makelog)


def run_stc(**kwargs):
    """Run StatTransfer .stc program"""

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('stc')
        if run.changedir:
            program = '"' + run.program + '"'
        else:
            program = '"' + run.program_full + '"'

        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['st']

        command = metadata.commands['st'] % (executable, program)

        run.execute_run(command)
    except:
        add_error_to_log(run.makelog)


def run_stcmd(**kwargs):
    """Run StatTransfer .stcmd program"""

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('stcmd')
        if run.changedir:
            program = '"' + run.program + '"'
        else:
            program = '"' + run.program_full + '"'

        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['st']

        command = metadata.commands['st'] % (executable, program)

        run.execute_run(command)
    except:
        add_error_to_log(run.makelog)


def run_lyx(**kwargs):
    """Export a LyX file to PDF

    e.g. To create pdf file for 'draft.lyx' with the log file being './make.log',
         use the command:
        `run_lyx(program = 'draft', makelog = './make.log')`
    """

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('lyx')
        program_name = run.program_name
        if run.changedir:
            program = '"' + run.program + '"'
        else:
            program = '"' + run.program_full + '"'
        
        # Get option
        option = run.option
        if not run.option:
            option = metadata.default_options['lyx']
            
        # Make handout/commented LyX file
        handout = run.handout
        comments = run.comments

        if handout or comments:
            program_name_suffix = '_handout' if handout else '_comments'
            temp_program_name = program_name + program_name_suffix
            temp_program_full = os.path.join(run.program_path, temp_program_name + '.lyx') 
            
            program = program.replace(program_name, temp_program_name)
            program_name = temp_program_name
            
            beamer = False
            shutil.copy2(run.program_full, temp_program_full)
            for line in fileinput.input(temp_program_full, inplace = True):
                if r'\textclass beamer' in line:
                    beamer = True
                elif handout and r'\options' in line and beamer:
                    line = line.rstrip('\n') + ', handout\n'
                elif comments and r'\begin_inset Note Note' in line:
                    line = line.replace('Note Note', 'Note Greyedout')
                print line,
        
        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['lyx']

        command = metadata.commands['lyx'] % (executable, option, program)

        run.execute_run(command)

        # Move PDF output
        pdfname = os.path.join(run.program_path, program_name + '.pdf')
        pdfout = run.pdfout
        if not '.pdf' in pdfout:
            pdfout = os.path.join(pdfout, program_name + '.pdf')
        if os.path.abspath(pdfname) != os.path.abspath(pdfout):
            shutil.copy2(pdfname, pdfout)
            os.remove(pdfname)
            
        # Remove handout/commented LyX file
        if handout or comments:
            os.remove(temp_program_full)

    except:
        add_error_to_log(run.makelog)


def run_rbatch(**kwargs):
    """Run an R batch program with log file"""

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('rbatch')

        # Get option
        option = run.option
        if not run.option:
            option = metadata.default_options['rbatch']
        if run.changedir:
            program = '"' + run.program + '"'
            default_log = os.path.join(run.program_path, run.program_name + '.Rout')
        else:
            program = '"' + os.path.join(run.program_path, run.program) + '"'
            default_log = os.path.join(os.getcwd(), run.program_name + '.Rout')

        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['rbatch']

        command = metadata.commands['rbatch'] % (executable, option, program, run.program_name + '.Rout')

        run.execute_run(command)
        run.move_log(default_log)
    except:
        add_error_to_log(run.makelog)


def run_rinstall(**kwargs):
    """Install an R package"""

    try:
        run = RunRPackageDirective(kwargs)
        run.error_check('rinstall')
        
        # Get option
        option = run.option
        if not run.option:
            option = metadata.default_options['rinstall']
            
        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['rinstall']

        command = metadata.commands['rinstall'] % (executable, option, run.lib, run.package)

        run.execute_run(command)
    except:
        add_error_to_log(run.makelog)


def run_sas(**kwargs):
    """Run a SAS script"""

    try:
        run = RunProgramDirective(kwargs)
        run.error_check('sas')

        # Get option
        option = run.option
        if not run.option:
            if run.osname != 'posix':
                option = metadata.default_options['saswin']

        # Get executable
        executable = run.executable
        if not run.executable:
            executable = metadata.default_executables['sas']

        # Get log, lst, and program
        if run.changedir:
            program = '"' + run.program + '"' 
            default_log = os.path.join(run.program_path, run.program_name + '.log')
            default_lst = os.path.join(run.program_path, run.program_name + '.lst')
        else:
            program = '"' + os.path.join(run.program_path, run.program) + '"'
            default_log = os.path.join(os.getcwd(), run.program_name + '.log')
            default_lst = os.path.join(os.getcwd(), run.program_name + '.lst')


        if run.osname == 'posix':
            command = metadata.commands['sas'] % (executable, option, program)
        else:
            command = metadata.commands['sas'] % (executable, program, option)

        run.execute_run(command)
        run.move_log(default_log)
        run.move_lst(default_lst)
    except:
        add_error_to_log(run.makelog)


def run_command(**kwargs):
    """Run a Shell command"""
    
    run = RunCommandDirective(kwargs)
    try:
        run.error_check('other')
        run.execute_run(run.command)
    except:
        add_error_to_log(run.makelog)
