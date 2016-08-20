#! /usr/bin/env python

import os
import re
import subprocess

import messages as messages
import metadata as metadata
from exceptionclasses import SyntaxError, LogicError

class LinkDirectives(object):

    def __init__(self, line, links_dir):
        self.line = line.replace('    ','\t')
        list_line = ((self.line.split('\t')+[None])[:2])        
        for i in xrange(len(list_line)):
            list_line[i] = list_line[i].strip()
        local, link = list_line
        
        self.linkeddir, self.linkedfile = os.path.split(link)
        if self.linkedfile == '':
            self.linkedfile = '*'
        
        self.localdir, self.localfile = os.path.split(local)
        if self.localdir == '':
            self.localdir = '.'
        if self.localfile == '':
            self.localfile = '""""'
            
        self.links_dir = links_dir
        
        self.error_check()
        self.clean()        
        self.create_flag_list()
        
    # Error Check
    def error_check(self):
        # Check syntax
        if self.linkeddir == '' or self.localdir=='':
            raise SyntaxError(messages.syn_error_noname)
        if not re.search('\*',self.linkedfile) and re.search('\*',self.localfile):
            raise SyntaxError(messages.syn_error_wildfilename1.replace('\n',''))
        if re.search('\*',self.localfile) and not re.search('\*$',self.localfile):
            raise SyntaxError(messages.syn_error_wildlocalfile.replace('\n',''))

    # Clean
    def clean(self):
        self.clean_syntax()
        self.clean_logic()

    def clean_syntax(self):
        # Clean slashes
        if self.localdir=='.' or self.localdir=='.\\':
            self.localdir = './'
        self.localdir = re.sub('^\.\\.*\\$', '^/.*/$', self.localdir)
        if not re.search('/$',self.localdir):
            self.localdir = self.localdir+'/'
            
        self.linkeddir = os.path.abspath(self.linkeddir)
        self.linkeddir = re.sub('^\.\\.*\\$', '^/.*/$', self.linkeddir)
        if not re.search('/$', self.linkeddir):
            self.linkeddir = self.linkeddir + '/'            

    def clean_logic(self):
        # Prepare prefix
        self.outprefix = ''
        if re.search('\*',self.localfile):
            self.outprefix = self.localfile[0:-1]

        # If localfile is left as a double quote, keep the same file name
        if self.localfile=='""""':
            self.localfile = self.linkedfile

        # Set file/localfile to empty if entire directory is operated on
        if self.linkedfile=='*':
            self.linkedfile = ''
            self.localfile = ''

        # Replace '.' in links.txt with inputted links directory location
        if self.localdir=='./':
            if self.linkedfile == '':
                dirname = os.path.split(os.path.dirname(self.linkeddir))[1]
                self.localdir = os.path.join(self.links_dir, dirname)
            else:
                self.localdir = self.links_dir
        else:
            self.localdir = self.links_dir + self.localdir
            
    def create_flag_list (self):
        self.flag_list = False
        if re.search('\*.+',self.linkedfile) or re.search('^.+\*',self.linkedfile) or (re.search('\*',self.localfile)):
            # Make wildcard list
            self.flag_list = True
            wildfirst,wildlast = self.linkedfile.split('*')
            self.LIST = []
            for element in os.listdir(self.linkeddir):
                if re.match('%s.*%s$' % (wildfirst,wildlast),element):
                    self.LIST.append(element.rstrip('\n'))       

        # Check wildcard directory non-empty
        if self.flag_list and not self.LIST:
            raise LogicError(messages.crit_error_emptylist)                    

    # Issue System Command
    def issue_sys_command(self, logfile, quiet):
        if self.flag_list:
            print >> logfile, messages.note_array % self.LIST
            for element in self.LIST:
                #Add prefix to localfile name (if none, then no change)
                self.localfile = self.outprefix+element
                self.linkedfile = element
                self.command(logfile, quiet)
        else:
            self.command(logfile, quiet)

    def command(self, logfile, quiet):
        if self.localfile == '':
            self.localdir = self.localdir.rstrip('/.')
        if self.linkeddir == '':
            self.linkeddir = self.linkeddir.rstrip('/.')
        if os.name == 'posix':
            command = metadata.commands['makelinkunix']
            options = (self.linkeddir, self.linkedfile, self.localdir, self.localfile)
        else:
            if self.linkedfile == '':
                option = '/d'
            else:
                option = ''        
            command = metadata.commands['makelinkwin']
            options = (option, self.localdir, self.localfile, self.linkeddir, self.linkedfile)
            
        # Following command contains try/except clause
        if quiet:
            subprocess.check_call(command % options, shell=True,
                                stdout=open(os.devnull, 'w'), 
                                stderr=open(os.devnull, 'w'))
        else:
            subprocess.check_call(command % options, shell=True)        
        
        print >> logfile, messages.success_makelink % (self.linkeddir, self.linkedfile,
                                                       self.localdir, self.localfile)
                                                            
    def add_to_dict(self, links_dict):
        if self.flag_list:
            for element in self.LIST:
                #Add prefix to localfile name (if none, then no change)
                self.localfile = self.outprefix+element
                self.linkedfile = element
                
                local = os.path.relpath(os.path.join(self.localdir, self.localfile))
                dest = os.path.join(self.linkeddir, self.linkedfile)
                links_dict[local] = dest
        else:  
            local = os.path.relpath(os.path.join(self.localdir, self.localfile))
            dest = os.path.join(self.linkeddir, self.linkedfile)
            links_dict[local] = dest
        return links_dict
