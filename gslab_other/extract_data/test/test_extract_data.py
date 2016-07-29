#! /usr/bin/env python

import sys, os, shutil, re

######################################################
# Preliminaries
######################################################

# Start logging
LOGFILE = open('./test_extract_data.log','wb')
print >> LOGFILE, 'Testing Started. Begin by testing success with legal input.\n'
orig_stderr = sys.stderr
sys.stderr = LOGFILE

# Define method to pass a given extract_data command to shell, and copy the log file
def test_cmd(cmd):
	test(cmd)
	copy_log()

# Test command	
def test(cmd):
	flag = os.system(cmd)
	if flag!=0:
		print >> LOGFILE, 'extract_data failed with input. Please see logfile below:'
	else:
		print >> LOGFILE, 'extract_data passed with input. Logfile below:'
		
# Copy output to logfile
def copy_log():
	print >> LOGFILE, '\n\n************************************\n\n'
	extract_data_log = open('./extract_data.log','rU')
	text = extract_data_log.read()
	LOGFILE.write(text)
	extract_data_log.close()
	os.remove('./extract_data.log')
	print >> LOGFILE, '\n\n************************************\n\n'
	
	
######################################################
# Test success with legal input
######################################################

# Run extract_data.py with legal externals.txt
print >> LOGFILE, 'Test extract_data completes with legal input.'
test_cmd('python ../py/extract_data.py -r ../test/sampledata/ -o ../test/')


######################################################
# Test failure with illegal command line syntax
######################################################

print >> LOGFILE, 'Now test extract_data breaks with illegal command line syntax.'

# Test non-existent externals.txt file, no externals.txt file, and no '-d' switch for
# non "../external/" directory
cmds = ['python ../py/extract_data.py -r ../test/incorrectfolder/ -o ../test/',
		'python ../py/extract_data.py',
		'python ../py/extract_data.py ../test/sampledata/ -o ../test/']

for line in cmds:
	print >> LOGFILE, 'Input at command line is \"%s\"' % line
	test_cmd(line)

	
######################################################
# Test failure with illegal binary input file
######################################################

print >> LOGFILE, 'Now test extract_data breaks with illegal binary input file.\n'

badfile_cmd='python ../py/extract_data.py -r ../test/sampledata_illegal/ -o ../test_illegal/'
print >> LOGFILE, 'Input at command line is \"%s\"' % badfile_cmd
test_cmd(badfile_cmd)

shutil.rmtree('../test_illegal/')

# Close log file
LOGFILE.close()
