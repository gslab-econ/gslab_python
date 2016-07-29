#! /usr/bin/env python

import sys, os, subprocess

def test_cmd(cmd):
	flag = subprocess.call(cmd)
	if flag != 0:
		print >> LOGFILE, 'speech_from_phrase failed.'
	else:
		print >> LOGFILE, 'speech_from_phrase passed.'

       
# Start logging
LOGFILE = open('../log/test_speech_from_phrase.log', 'wb')
print >> LOGFILE, 'Testing Started:\n'
orig_stderr = sys.stderr
sys.stderr = LOGFILE
	
######################################################
# Test success: Legal syntax
######################################################

# Run speech_from_phrase.py with legal syntax
print >> LOGFILE, '[[TEST GOOD]]'
print >> LOGFILE, 'Test speech_from_phrase completes with legal syntax.'

cmds = ['python ../code/speech_from_phrase.py "naval store" 60 "../log"',
		'python ../code/speech_from_phrase.py "welfar system" 104 "../log" "GPO"']
        
for line in cmds:
	print >> LOGFILE, 'Input at command line is \"%s\"' % line
	test_cmd(line)

print >> LOGFILE, '\n\n'

######################################################
# Test failure: Bad command line syntax
######################################################

print >> LOGFILE, '[[TEST BAD]]'
print >> LOGFILE, 'Now test speech_from_phrase breaks with illegal command line syntax.'

cmds = ['python ../code/speech_from_phrase.py',
		'python ../code/speech_from_phrase.py "naval store" 60 "../non_existent_dir"',
		'python ../code/speech_from_phrase.py "naval store" 200',
        'python ../code/speech_from_phrase.py "naval" 60 "../log"']

for line in cmds:
	print >> LOGFILE, 'Input at command line is \"%s\"' % line
	test_cmd(line)

LOGFILE.close()
