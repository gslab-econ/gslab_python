#! /usr/bin/env python
		
######################################################
# Define Messages
######################################################		
	
# 1) Critical Errors
crit_error_log = 'ERROR! Cannot open logfile %s'
crit_error_badoption = 'ERROR! option not recognized: %s %s'
crit_error_missingoption = 'ERROR! requires both -r and -o options!'
crit_error_norawfolder = 'ERROR! Raw folder %s does not exist'
crit_error_outputdirfail = 'ERROR! Cannot create output directory at %s'
crit_error_readfail = 'ERROR! cannot read a line... perhaps a non-text file?'

# 2) Timing messages
time_logstart = '\nextract_data.py started: %s%s\n'
time_logend = '\nextract_data.py ended: %s\n'
time_filetime = 'time to process file %s was %s seconds.'
time_charfiletime = 'time to process characteristics file: %s seconds.'
time_csvsorttime = 'time to sort csv was %s seconds.'

# 3) Notes
note_rawdir = 'Raw folder: %s'
note_outdir = 'Output folder: %s'
note_reading = 'Reading from %s'
note_written = 'Data written to %s'
