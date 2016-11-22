#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
import gslab_make.private.messages as messages
from gslab_make import start_make_logging, add_log, clear_dirs
from gslab_make.private import CritError
from gslab_make.tests import nostderrout
    

class testAddLog(unittest.TestCase):

    def setUp(self):
        makelog_file = '../output/make.log'
        output_dir = '../output/'
        with nostderrout():
            clear_dirs(output_dir)
            start_make_logging(makelog_file)

    def test_add(self):
        add_one = 'Added line 1 \n'
        add_one_file = '../output/add1.txt'
        outfile = open(add_one_file, 'wb')
        outfile.write( ''.join(add_one) )
        outfile.close()        
        add_two = 'Added line 2 \n'
        add_two_file = '../output/add2.txt'
        outfile = open(add_two_file, 'wb')
        outfile.write( ''.join(add_two) )
        outfile.close()
        with nostderrout():
            add_log(add_one_file, add_two_file, makelog = '../output/make.log')
        logfile_data = open('../output/make.log', 'rU').readlines()
        self.assertEqual(logfile_data[-2], 'Added line 1 \n')
        self.assertEqual(logfile_data[-1], 'Added line 2 \n')
        
    def test_nofile(self):
        self.assertFalse(os.path.isfile('../output/add1.txt'))
        with nostderrout():
            add_log('../output/add1.txt', makelog = '../output/make.log')
        logfile_data = open('../output/make.log', 'rU').read()      
        message = messages.note_nofile % '../output/add1.txt'
        self.assertIn(message, logfile_data)    

    def test_nolog(self):
        add_one = 'Added line 1 \n'
        add_one_file = '../output/add1.txt'
        outfile = open(add_one_file, 'wb')
        outfile.write( ''.join(add_one) )
        outfile.close()
        os.remove('../output/make.log')
        with nostderrout():        
            with self.assertRaises(CritError):
                add_log('../output/add1.txt', makelog = '../output/make.log')        

    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
    
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
