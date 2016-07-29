#! /usr/bin/env python

import unittest, sys, os, shutil, contextlib
sys.path.append('..')
from py.make_log import start_make_logging, del_log
from py.dir_mod import clear_dirs
from py.private.exceptionclasses import CritError
import py.private.messages as messages
from nostderrout import nostderrout
    
    
class testDelLog(unittest.TestCase):

    def setUp(self):
        makelog_file = '../output/make.log'
        output_dir = '../output/'
        with nostderrout():
            clear_dirs(output_dir)
            start_make_logging(makelog_file)
        log_to_del = 'Delete this file \n'
        log_to_del_file = 'del_log.txt'
        outfile = open(log_to_del_file, 'wb')
        outfile.write( ''.join(log_to_del) )
        outfile.close()        

    def test_del(self):
        self.assertTrue(os.path.isfile('del_log.txt'))
        with nostderrout():
            del_log('del_log.txt', makelog = '../output/make.log')
        self.assertFalse(os.path.isfile('del_log.txt'))

    def test_nofile(self):
        os.remove('del_log.txt')
        with nostderrout():
            del_log('del_log.txt', makelog = '../output/make.log')    
        logfile_data = open('../output/make.log', 'rU').read()      
        message = messages.note_nofile % 'del_log.txt'
        self.assertIn(message, logfile_data) 
        
    def test_nolog(self):
        os.remove('../output/make.log')
        with nostderrout():
            with self.assertRaises(CritError):
                del_log('del_log.txt', makelog = '../output/make.log')
        
    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
        if os.path.isfile('del_log.txt'):
            os.remove('del_log.txt')
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()