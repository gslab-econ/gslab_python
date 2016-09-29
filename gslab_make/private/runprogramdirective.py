#! /usr/bin/env python

import os
import re
import shutil
import subprocess

from exceptionclasses import CustomError, CritError, SyntaxError, LogicError
import messages as messages
import metadata as metadata

######################################################
# Run Program Directive
######################################################

class RunProgramDirective(object):


    def __init__(self, kwargs, program_bool = True):
        dict((k.lower(), v) for k, v in kwargs.iteritems())

        if program_bool:
            if 'program' in kwargs.keys():
                program_input = kwargs['program']
                self.program_path = os.path.dirname(program_input)
                program_base = os.path.basename(program_input)
                self.program_name, self.program_ext = os.path.splitext(program_base)
            else:
                raise SyntaxError(messages.syn_error_noprogram)

            if self.program_path == '':
                self.program_path = './'
        else:
            self.program_ext = ''

        if 'makelog' in kwargs.keys():
            self.makelog = kwargs['makelog']
            if self.makelog:
                self.makelog = os.path.abspath( self.makelog )
        else:
            self.makelog = os.path.abspath( metadata.settings['makelog_file'] )

        if 'option' in kwargs.keys():
            self.option = kwargs['option']
            self.option_dict = self.parse_options()
            self.option_overlap_error_check(kwargs)
        else:
            self.option = '';
            self.option_dict = {}

        if 'log' in kwargs.keys():
            self.log = os.path.abspath( kwargs['log'] )
        else:
            self.log = self.option_assigned('log', '')

        if 'lst' in kwargs.keys():
            self.lst = os.path.abspath( kwargs['lst'] )
        else:
            self.lst = self.option_assigned('lst', metadata.settings['output_dir'])

        if 'changedir' in kwargs.keys():
            self.changedir = kwargs['changedir']
        else:
            self.changedir = False

        if 'executable' in kwargs.keys():
            self.executable = kwargs['executable']
        else:
            self.executable = '';

        if 'args' in kwargs.keys():
            self.args = kwargs['args']
        else:
            self.args = '';

        if 'handout' in kwargs.keys():
            self.handout = kwargs['handout']
        else:
            self.handout = False
            
        if 'comments' in kwargs.keys():
            self.comments = kwargs['comments']
        else:
            self.comments = False
            
        if 'pdfout' in kwargs.keys():
            self.pdfout = os.path.abspath( kwargs['pdfout'] )
        else:
            pdfout_dir = ''
            if self.handout or self.comments:
                pdfout_dir = metadata.settings['temp_dir']
            else:
                pdfout_dir = metadata.settings['output_dir']
            self.pdfout = self.option_assigned('pdfout', pdfout_dir)

        self.osname = os.name
        self.option = self.update_option()


    def parse_options(self):
        option_list = self.option.strip().replace("=", " ").split()
        option_dict = {}
        for opt in option_list:
            if opt:
                if opt[0] in metadata.option_start_chars:
                    option = opt
                    option_dict[option] = ''
                else:
                    option_dict[option] += opt + ' '

        return option_dict


    def option_overlap_error_check(self, kwargs):
        prog = [prog for prog, ext in metadata.extensions.iteritems() if ext == self.program_ext][0]
        option_overlaps = metadata.option_overlaps.get(prog)
        if not option_overlaps: return
        for opt in option_overlaps:
            if self.option_dict.has_key(option_overlaps[opt]) and kwargs.has_key(opt):
                raise CritError(messages.crit_error_option_overlap
                                % (opt, option_overlaps[opt]))


    def option_assigned(self, option, default):
        assigned_value = default

        prog = [prog for prog, ext in metadata.extensions.iteritems() if ext == self.program_ext][0]
        option_overlaps = metadata.option_overlaps.get(prog)
        if option_overlaps:
            replace_option = option_overlaps.get(option)
            if replace_option:
                value = self.option_dict.get(replace_option)
                if value:
                    print messages.note_option_replaced % (replace_option, option)
                    del self.option_dict[replace_option]
                    assigned_value = value

        return assigned_value


    def update_option(self):
        prog = [prog for prog, ext in metadata.extensions.iteritems() if ext == self.program_ext][0]
        if prog in metadata.option_overlaps.keys():
            option = ''
            for opt, arg in self.option_dict.iteritems():
                option += str(opt + ' ' + arg + ' ')
            return option
        else:
            return self.option


    def error_check(self, prog):
        if (self.osname != 'posix') & (self.osname != 'nt'):
            raise CritError(messages.crit_error_unknown_system % self.osname)

        ext = metadata.extensions[prog]
        if self.program_ext == '':
            self.program_ext = ext

        if self.program_ext:
            self.program = self.program_name + self.program_ext
            self.program_full = os.path.join(self.program_path, self.program)

            if not os.path.isfile(self.program_full):
                raise CritError(messages.crit_error_no_file % self.program_full)
            if self.program_ext != ext:
                raise CritError(messages.crit_error_extension % self.program_full)


    def execute_run(self, command):
        print '\n'
        current_directory = os.getcwd()

        if self.changedir:
            os.chdir(self.program_path)

        if not self.log:
            tempname = current_directory + '/make-templog.txt'
        else:
            tempname = os.path.abspath(self.log)
        TEMPFILE = open(tempname, 'wb')            

        if self.makelog:
            if not (metadata.makelog_started and os.path.isfile(self.makelog)):
                raise CritError(messages.crit_error_nomakelog % self.makelog)

            # Open main log file
            try:
                LOGFILE = open(self.makelog, 'ab')
            except Exception as errmsg:
                print errmsg
                raise CritError(messages.crit_error_log % self.makelog)

            try:
            # Execute command and print content to LOGFILE
                print 'Executing: ', command
                print >>LOGFILE, '\n\nExecute: ', command
                subprocess.check_call(command, shell = True, stdout = TEMPFILE, stderr = TEMPFILE)
                TEMPFILE.close()
                LOGFILE.write(open(tempname, 'rU').read())
                LOGFILE.close()
            except Exception as errmsg:
            # If fails then print errors to LOGFILE
                TEMPFILE.close()
                LOGFILE.write(open(tempname, 'rU').read())
                print messages.crit_error_bad_command % command, '\n', str(errmsg)
                print >> LOGFILE, messages.crit_error_bad_command % command, '\n', str(errmsg)
                LOGFILE.close()
        else:
            try:
            # Execute command
                print 'Executing: ', command
                subprocess.check_call(command, shell = True, stdout = TEMPFILE, stderr = TEMPFILE)
                TEMPFILE.close()
            except Exception as errmsg:
            # If fails then print errors
                TEMPFILE.close()
                print messages.crit_error_bad_command % command, '\n', str(errmsg)
                print >> TEMPFILE, messages.crit_error_bad_command % command, '\n', str(errmsg)

        if not self.log:
            os.remove(tempname)
        if self.changedir:
            os.chdir(current_directory)


    def move_log(self, default_log):
        if self.makelog:
            if not (metadata.makelog_started and os.path.isfile(self.makelog)):
                raise CritError(messages.crit_error_nomakelog % self.makelog)
            if os.path.abspath(default_log) != os.path.abspath(self.log):
                # Append default_log to main log
                LOGFILE = open(self.makelog, 'ab')
                try:
                    LOGFILE.write(open(default_log, 'rU').read())
                except Exception as errmsg:
                    print errmsg
                    raise CritError(messages.crit_error_no_file % default_log)
                LOGFILE.close()

        # Save default_log as self.log
        if self.log:
            shutil.copy2(default_log, self.log)
        os.remove(default_log)


    def move_lst(self, default_lst):
        if not (os.path.isfile(default_lst)): return

        if self.makelog:
            if not (metadata.makelog_started and os.path.isfile(self.makelog)):
                raise CritError(messages.crit_error_nomakelog % self.makelog)

            if os.path.abspath(default_lst) != os.path.abspath(self.lst):
                # Append default_lst to main log
                LOGFILE = open(self.makelog, 'ab')
                try:
                    LOGFILE.write(open(default_lst, 'rU').read())
                except Exception as errmsg:
                    print errmsg
                    raise CritError(messages.crit_error_no_file % default_lst)
                LOGFILE.close()

        # Save default_lst as self.lst
        if self.lst:
            shutil.copy2(default_lst, self.lst)

        os.remove(default_lst)


######################################################
# Run R Package Directive
######################################################

class RunRPackageDirective(RunProgramDirective):


    def __init__(self, kwargs, program_bool = False):
        RunProgramDirective.__init__(self, kwargs, program_bool)

        if 'package' in kwargs.keys():
            self.package = kwargs['package']
            self.package = re.sub('\\\\', '/', self.package)
        else:
            raise SyntaxError(messages.syn_error_nopackage)

        if 'lib' in kwargs.keys():
            self.lib = '-l ' + kwargs['lib']
        else:
            self.lib = ''

    def error_check(self, prog):
        if (self.osname != 'posix') & (self.osname != 'nt'):
            raise CritError(messages.crit_error_unknown_system % self.osname)

        if self.package and not os.path.isfile(self.package):
            raise CritError(messages.crit_error_no_package % self.package)


######################################################
# Run Command Directive
######################################################

class RunCommandDirective(RunProgramDirective):


    def __init__(self, kwargs, program_bool = False):
        RunProgramDirective.__init__(self, kwargs, program_bool)

        if 'command' in kwargs.keys():
            self.command = kwargs['command']
            self.command = re.sub('\\\\', '/', self.command)
        else:
            raise SyntaxError(messages.syn_error_nocommand)

