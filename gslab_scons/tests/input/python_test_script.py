#! /usr/bin/env python
import sys

try:
	arg = sys.argv[1]
except:
	arg = ''
	
if arg != '':
    message = arg
else:
    message = 'Test Output \n'
output_name = 'output.txt'
outfile = open(output_name, 'wb')
outfile.write( ''.join(message) )
outfile.close()

print "Test script complete"