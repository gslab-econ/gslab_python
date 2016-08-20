#! /usr/bin/env python

import os, shutil, fileinput

import private.metadata as metadata
import private.messages as messages
from private.exceptionclasses import SyntaxError
from private.runprogramdirective import RunProgramDirective, RunCommandDirective, RunRPackageDirective
from private.preliminaries import add_error_to_log

###############################################################
# Run Stata, Matlab, Perl, Python, StatTransfer
# Mathematica, RInstall, RBatch
###############################################################

def run_stata(**kwargs):
    """Run Stata program with log file

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run Matlab program with log file

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run Perl program

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run Python program

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run Mathematica program

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run StatTransfer .stc program

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run StatTransfer .stcmd program

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run Lyx export to Pdf

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run R batch program with log file

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Install R package

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run SAS script

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

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
    """Run a Shell command

    Please see /trunk/lib/python/gslab_make/py/readme_make.txt for more explanations."""

    run = RunCommandDirective(kwargs)
    try:
        run.error_check('other')
        run.execute_run(run.command)
    except:
        add_error_to_log(run.makelog)
