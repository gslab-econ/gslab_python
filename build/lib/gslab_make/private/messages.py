#! /usr/bin/env python
		
######################################################
# Define Messages
######################################################		
	
# 1) Critical Errors
crit_error_log = 'ERROR! Cannot open logfile %s'
crit_error_nomakelog = 'ERROR! Makelog %s not found (either not started or deleted)'
crit_error_log_header = 'ERROR! %s is not a log of %s (first line should be "%s")'
crit_error_links_header = 'ERROR! %s is not a links file (first line should be "%s")'
crit_error_extfile = 'ERROR! Cannot open externals file %s' 
crit_error_file = 'ERROR! Cannot open file %s'
crit_error_emptylist = '''ERROR! Source directory, and/or matched list, is empty. Please check.'''
crit_error_copyincomplete = 'COPY ERROR! Copy not complete on %s%s.' 
crit_error_extension = 'ERROR! %s%s does not have the right program extension'
crit_error_no_file = 'ERROR! File %s not found'
crit_error_unknown_system = 'ERROR! The program syntax for system %s is not defined'
crit_error_bad_command = 'ERROR! Command %s executed with errors'
crit_error_no_directory = 'ERROR! Directory %s does not exist'
crit_error_no_dta_file = 'Error! DTA output file %s is not listed in the manifest file %s.'
crit_error_option_overlap = 'ERROR! Option %s and command line option %s overlap'
crit_error_no_package = 'ERROR! R package %s not found'
crit_error_github = 'ERROR! Unable to reach github API at %s. Check token and url.'
crit_error_assetid = 'ERROR! Unable to determine asset id for %s in release %s. Check url and token.'

# 2) Syntax Errors
syn_error_revnum =  'ERROR! Revision number %s for %s%s is not a valid number.'
syn_error_noname = 'ERROR! No file/outfile/outdir name given.'
syn_error_wildfilename = '''ERROR! In externals text file, a prefix can only be set for lines with 
a wildcard in the file column (single files can simply be renamed).'''
syn_error_wildoutfile = '''ERROR! When specifying an outfile wildcard, \'*\' must occur at end 
of column (i.e., we only allow prefixes).'''
syn_error_noprogram = '''ERROR! This call must take an argument program = "program_name"'''
syn_error_nopackage = '''ERROR! This call must take an argument package = "package_name"'''
syn_error_nocommand = '''ERROR! An argument command = "" must be specified to run the Shell command'''
syn_error_manifest = r'Error in %s! All lines that start with "File:" should have a valid file path'
syn_error_url = 'ERROR! Incorrect url format. Please check externals_github and see associated readme.'

# 3) Logical Errors
logic_error_revdir = '''ERROR! At line %s%s - source path and revision number must both be defined 
or be undefined. Currently, %s%s.'''
logic_error_firstrevdir = 'ERROR! First rev/dir pair cannot be left blank.'

# 4) Notes & Warnings
note_logstart = '\n %s started:' 
note_makelogstart = '\n make.py started:'
note_logend = '\n %s ended:'
note_makelogend = '\n make.py ended:'
note_extfilename = 'Note: not using filename externals.txt.\n'
note_extdir_nofound = 'Note: %s not found.\n' 
note_input = '\n Input was: "%s".'
note_svnfail = 'Svn Export unsuccessful on %s%s. Please check externals file.'
note_array = '''Subset of folder, prefixed group of files, or entire folder if rev=COPY, to be exported.
The array is: %s.'''
note_nofile = '\n File %s does not exist.\n'
note_no_csv_file = '\n Warning! CSV output file %s is not listed in the manifest file %s.'
note_no_txt_file = '\n Warning! TXT output file %s is not listed in the manifest file %s.'
note_option_replaced = '\n Note: replacing command line option %s with option %s.\n'

# 5) Successes 
success_del_extdir = '%s successfully deleted.\n' 
success_create_extdir = '%s successfully (re)created.\n' 
success_svn = 'SVN command passed: %s%s @%s exported to %s%s.' 
success_makelink = 'Symlink successfully created. Source: %s%s\tLocal location: %s%s.'
success_copy = 'COPY command passed: %s%s copied to %s%s.'
success_github = 'GitHub command passed: %s exported to %s%s.'
