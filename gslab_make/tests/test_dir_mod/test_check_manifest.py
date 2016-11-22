#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_make import (check_manifest, clear_dirs, start_make_logging,
                        run_stata, get_externals)
from gslab_make.private import CritError
from gslab_make.tests import nostderrout

    
class testCheckManifest(unittest.TestCase):

    def setUp(self):
        makelog_file = '../output/make.log'
        output_dir   = '../output/'
        external_dir = '../external/'
        with nostderrout():
            clear_dirs(output_dir, external_dir)
            start_make_logging(makelog_file)
        with nostderrout():
            get_externals('./input/externals_stata_ado.txt', 
                          '../external/', '', quiet = True)
            run_stata(program = './input/stata_test_script.do',
                      makelog_file = makelog_file)
     
    def test_manifest_ok(self):
        manifest_file = '../output/data_file_manifest.log'
        with nostderrout():
            check_manifest(manifest_file, '../output/', '../output/make.log')
        self.assertTrue(self.check_results('../output/make.log', 0, 0))       
    
    def test_manifest_error(self):
        manifest_file = '../output/data_file_manifest.log'
        self.remove_manifest_entry(manifest_file, 1)
        with nostderrout():
            check_manifest(manifest_file, '../output/', '../output/make.log')
        self.assertTrue(self.check_results('../output/make.log', 1, 0))

    def test_manifest_warning(self):
        manifest_file = '../output/data_file_manifest.log'
        self.remove_manifest_entry(manifest_file, 3)
        with nostderrout():
            check_manifest(manifest_file, '../output/', '../output/make.log')
        self.assertTrue(self.check_results('../output/make.log', 0, 1))     
        
    def remove_manifest_entry(self, manifest, entry_to_remove):
        manifest_data = open(manifest, 'rU').readlines()
        removed = 0
        fileno = 0
        for line in manifest_data:
            if removed == 0:
                if line.startswith('File:'):
                    fileno += 1
                    if fileno == entry_to_remove:
                        manifest_data.remove(line)
                        removed = 1
        outfile = open(manifest, 'wb')
        outfile.write( ''.join(manifest_data) )
        outfile.close()
        
    def check_results(self, logfile, num_errors, num_warnings):
        logfile_data = open(logfile, 'rU').readlines()
        errors = 0
        warnings = 0
        for line in logfile_data:
            if line.startswith(' Warning!'):
                warnings += 1
                if warnings > num_warnings:
                    return False
            if line.startswith('CritError:'):
                errors += 1
                if errors > num_errors:
                    return False      
        return (warnings == num_warnings and errors == num_errors)         
    
    def test_no_makelog(self):
        manifest_file = '../output/data_file_manifest.log'
        shutil.rmtree('../output/')
        with nostderrout():
            with self.assertRaises(CritError):
                check_manifest(manifest_file, '../output/')
        
    def test_no_manifest_file(self):
        manifest_file = '../output/data_file_manifest.log'
        os.remove(manifest_file)
        with nostderrout():
            check_manifest(manifest_file, '../output/')  
        logfile_data = open('../output/make.log', 'rU').readlines()
        self.assertTrue(logfile_data[-1].startswith('CritError:'))
        
    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
        if os.path.isdir('../external/'):
            shutil.rmtree('../external/')            
        if os.path.isfile('get_externals.log'):
            os.remove('get_externals.log') 
    

if __name__ == '__main__':
    os.getcwd()
    unittest.main()