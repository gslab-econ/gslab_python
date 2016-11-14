#! /usr/bin/env python

import os
import re
import shutil 
import subprocess
import urlparse

import messages as messages
import metadata as metadata
from exceptionclasses import CustomError, CritError, SyntaxError, LogicError

######################################################
# System Directive
######################################################

class SystemDirective(object):

    def __new__(cls, raw, LOGFILE, last_dir, last_rev, token = "@NONE@"):
        if raw.split('\t',1)[0]!='COPY':
            if token != "@NONE@":
                return super(SystemDirective,cls).__new__(GitHubDirective)
            else:
                return super(SystemDirective,cls).__new__(SvnExportDirective)
        else:
            return super(SystemDirective,cls).__new__(CopyDirective)

    def __init__(self, raw, LOGFILE, last_dir, last_rev, token = "@NONE@"):
        self.logfile = LOGFILE
        # Print raw input to logfile
        print >> self.logfile, messages.note_input % raw
        # Split columns
        self.raw = raw.replace('    ','\t')
        list = ((self.raw.split('\t')+[None])[:5])
        for i in xrange(len(list)):
            list[i] = list[i].strip()
        self.rev,self.dir,self.file,self.outdir,self.outfile = list
        # Load previous rev/dir if empty 
        if self.dir=='' and self.rev=='':
            self.dir = last_dir
            self.rev = last_rev
        if not re.search('/$', self.dir):
            self.dir = self.dir + '/'
        # Flag if wildcard list needs to be compiled in subclass
        self.flag_list = []
        if re.search('\*.+',self.file) or re.search('^.+\*',self.file) or (re.search('\*',self.outfile)):
            self.flag_list = 1

    # Error Check
    def error_check(self):
        self.error_check_SVN()
        self.error_check_local()        
        
    def error_check_SVN(self):    
        # Check that rev/dir are well-defined
        if self.dir=='' and self.rev=='':
            if self.last_rev=='' or self.last_dir=='':
                raise LogicError(messages.logic_error_firstrevdir)
    
    def error_check_local(self):
        # Check syntax
        if self.file=='' or self.outfile=='' or self.outdir=='':
            raise SyntaxError(messages.syn_error_noname)
        if not re.search('\*',self.file) and re.search('\*',self.outfile):
            raise SyntaxError(messages.syn_error_wildfilename1.replace('\n',''))
        if re.search('\*',self.outfile) and not re.search('\*$',self.outfile):
            raise SyntaxError(messages.syn_error_wildoutfile.replace('\n',''))
        if len(re.findall('\*',self.outfile)) > 1:
            raise SyntaxError(messages.syn_error_wildoutfile.replace('\n',''))
            
        # Check wildcard directory non-empty
        if self.flag_list and not self.LIST:
            raise LogicError(messages.crit_error_emptylist)

    # Clean
    def clean(self, externals_dir):
        self.clean_syntax()
        self.clean_logic(externals_dir)

    def clean_syntax(self):
        # Clean slashes
        if self.outdir=='.' or self.outdir=='.\\':
            self.outdir = './'
        self.outdir = re.sub('^\.\\.*\\$', '^/.*/$', self.outdir)
        if not re.search('/$',self.outdir):
            self.outdir = self.outdir+'/'

    def clean_logic(self, externals_dir):
        # Replace default value
        if externals_dir == '@DEFAULTVALUE@':
            externals_dir = metadata.settings['external_dir']
        
        # Replace '.' in externals.txt with inputted externals directory location
        if self.outdir=='./':
            self.outdir = externals_dir
        else:
            self.outdir = externals_dir+self.outdir

        # Prepare prefix
        self.outprefix = ''
        if re.search('\*',self.outfile):
            self.outprefix = self.outfile[0:-1]

        # If outfile is left as a double quote, keep the same file name
        if self.outfile=='""""':
            self.outfile = self.file

        # Set file/outfile to empty if entire directory is operated on
        if self.file=='*':
            self.file = ''
            self.outfile = ''

    # Issue System Command
    def issue_sys_command(self, quiet):
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        if self.flag_list:
            print >> self.logfile, messages.note_array % self.LIST
            for element in self.LIST:
                #Add prefix to outfile name (if none, then no change)
                self.outfile = self.outprefix+element
                self.file = element
                self.command(quiet)
        else:
            self.command(quiet)

    def command(self, quiet):
        # Define individually for each subclass
        pass

######################################################
# GitHub Directive
######################################################

class GitHubDirective(SystemDirective):

    def __init__(self, raw, LOGFILE, last_dir, last_rev, token):
        self.logfile = LOGFILE
        # Print raw input to logfile
        print >> self.logfile, messages.note_input % raw
        # Split columns
        self.raw = raw.replace('    ','\t')
        list = ((self.raw.split('\t')+[None])[:3])
        for i in xrange(len(list)):
            list[i] = list[i].strip()
        self.url,self.outdir,self.outfile = list
        self.token = token
        self.get_asset_data()
       
        # Flag if wildcard list needs to be compiled in subclass
        self.flag_list = []
        if re.search('\*.+',self.file) or re.search('^.+\*',self.file) or (re.search('\*',self.outfile)):
            self.flag_list = 1
    
    # Obtain asset id and create download url
    def get_asset_data(self):
        import requests
        split_url   = urlparse.urlsplit(self.url)
        path        = split_url.path
        path        = path.split("/")
        clean_path  = []
        assetid     = None

        for i in range(len(path)):
            if bool(path[i]):
                clean_path.append(path[i])
        if len(clean_path) != 6:
            raise SyntaxError(messages.syn_error_url)
        
        organization, repo, releases, download, tag, assetname = clean_path
        prelim_path         = "https://" + self.token + ":@api.github.com/repos/"
        paste_prelim        = "https://" + "[token]"  + ":@api.github.com/repos/"
        releasepath         = prelim_path  + organization + "/" + repo + "/" + \
                              releases + "/" + "tags" + "/" + tag
        releasepath_paste   = paste_prelim + organization + "/" + repo + "/" + \
                              releases + "/" + "tags" + "/" + tag

        # Accessing GitHub API for asset ID
        try:
            s               = requests.session()    
            json_release    = s.get(releasepath)
            json_output     = json_release.content
            json_split      = json_output.split(",")
            json_name       = '"name":"' + assetname + '"'
        except:
            raise CritError(messages.crit_error_github % releasepath_paste)
    
        # Finding asset ID in JSON output
        for i in range(len(json_split)):
            if json_split[i] == json_name:
                assetid = json_split[i - 1]
                assetid = assetid.split(":")
                assetid = assetid[1]
    
        # Creating download url
        if assetid is None:
            raise CritError(messages.crit_error_assetid % (assetname, tag))
        else:
            assetpath       = prelim_path  + organization + "/" + repo + "/" + \
                              releases + "/" + "assets" + "/" + assetid
            paste_assetpath = paste_prelim + organization + "/" + repo + "/" + \
                              releases + "/" + "assets" + "/" + assetid
        
        self.url        = assetpath
        self.paste_url  = paste_assetpath
        self.file       = assetname
    
    # Error Check
    def error_check(self):
        self.error_check_local()        

    # Define GitHubExport Command    
    def command(self, quiet):
        # Following command contains try/except clause
        if quiet:
            self.github_download()
        else:
            self.github_download()    
            print >> self.logfile, messages.success_github % (self.paste_url, self.outdir, 
                                                              self.outfile)
    
    # Download Asset
    def github_download(self):
        import requests
        filename = '%s%s' % (self.outdir, self.outfile)
        header   = {"Accept": "application/octet-stream"}
        s        = requests.session()
        s.post(self.url)
        asset    = s.get(self.url, headers = header)
        f        = open(filename, "wb")
        f.write(asset.content)
        f.close()   
    
######################################################
# SvnExport Directive
######################################################

class SvnExportDirective(SystemDirective):

    def __init__(self, raw, LOGFILE, last_dir, last_rev, token = '@NONE@'):
        SystemDirective.__init__(self, raw, LOGFILE, last_dir, last_rev)
        # Fill in placemarkers
        self.dir = re.sub('\%svn\%',metadata.file_loc['svn'],self.dir)
        self.dir = re.sub('\%svnbranch\%',metadata.file_loc['svnbranch'],self.dir)
        self.dir = re.sub('\%svn_retail2\%',metadata.file_loc['svn_retail2'],self.dir)
        self.dir = re.sub('\%svnbranch_retail2\%',metadata.file_loc['svnbranch_retail2'],self.dir)
        # Make wildcard list
        if self.flag_list:
            svnlist = 'svn list \"%s@%s\"' % (self.dir,self.rev)
            LISTSVN = os.popen(svnlist).readlines()
            wildfirst,wildlast = self.file.split('*')
            self.LIST = []
            for element in LISTSVN:
                if re.match('%s.*%s$' % (wildfirst,wildlast),element):
                    self.LIST.append(element.rstrip('\n'))

    # Error Check
    def error_check(self):
        if not re.match('\d+$',self.rev) and self.rev!='':
            raise SyntaxError(messages.syn_error_revnum % (self.rev,self.dir,self.file))
        if self.dir=='' and self.rev!='' or self.dir!='' and self.rev=='':
            raise LogicError(messages.logic_error_revdir.replace('\n','') % (self.dir,self.file,
                            self.rev,self.dir))

 
        SystemDirective.error_check(self)

    # Define SvnExport Command    
    def command(self, quiet):
        # Following command contains try/except clause
        if quiet:
            subprocess.check_call(metadata.commands['svnexport'] % (self.rev, self.dir, self.file,
                                                                    self.rev, self.outdir, self.outfile), 
                                  shell = True, stdout = open(os.devnull, 'w'), stderr = open(os.devnull, 'w'))
        else:
            subprocess.check_call(metadata.commands['svnexport'] % (self.rev, self.dir, self.file,
                                                                    self.rev, self.outdir, self.outfile), 
                                  shell = True)

        print >> self.logfile, messages.success_svn % (self.dir, self.file, self.rev,
                                                       self.outdir, self.outfile)

######################################################
# Copy Directive
######################################################

class CopyDirective(SystemDirective):

    def __init__(self, raw, LOGFILE, last_dir, last_rev, token = '@NONE@'):
        SystemDirective.__init__(self, raw, LOGFILE, last_dir, last_rev)
        # Deal with any directory itemwise
        if re.search('\*',self.file):
            self.flag_list = 1
        # Fill in placemarkers, and dir if empty
        if self.dir=='':
            self.dir = self.last_dir
        for key in metadata.file_loc:
            self.dir = re.sub('\%%%s\%%' % key,metadata.file_loc[key],self.dir)
        # Ensure legal slashes
        self.dir = self.dir.replace('/','\\')
        # Make wildcard list
        if self.flag_list:
            self.LIST = os.listdir(self.dir)

    # Error Check
    def check_revdir(self):
        if self.dir=='' and self.last_dir=='':
            raise LogicError(messages.logic_error_firstrevdir)


        SystemDirective.check_revdir(self)

    # Define Copy Command        
    def command(self, quiet):
        try:
            shutil.copy('%s%s' % (self.dir, self.file),'%s%s' % (self.outdir, self.outfile))
            print >> self.logfile, messages.success_copy  % (self.dir, self.file, 
                                                             self.outdir, self.outfile)
        except:
            raise CritError(messages.crit_error_copyincomplete % (self.dir,self.file))
