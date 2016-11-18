#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_make import (start_make_logging, set_option, end_make_logging,
                        check_manifest, clear_dirs, get_externals, run_stata)
from gslab_make.tests import nostderrout
import gslab_make.private.metadata as metadata

class testSetOption(unittest.TestCase):

    def setUp(self):
        pass

    def test_set_option(self):
        with nostderrout():
            set_option(makelog = '../customoutput/custommake.log', 
                       temp_dir = '../customtemp/', 
                       output_dir = '../customoutput/',
                       manifest = '../customoutput/data_file_manifest.log')
        
        self.assertEqual(metadata.settings['makelog_file'], 
                         '../customoutput/custommake.log')
        self.assertEqual(metadata.settings['temp_dir'], 
                         '../customtemp/')
        self.assertEqual(metadata.settings['output_dir'], 
                         '../customoutput/')
        self.assertEqual(metadata.settings['manifest_file'], 
                         '../customoutput/data_file_manifest.log')
    
    def tearDown(self):
        with nostderrout():
            set_option(makelog    = '../output/make.log', 
                       temp_dir   = '../temp/', 
                       output_dir = '../output/',
                       manifest   = '../output/data_file_manifest.log')


if __name__ == '__main__':
    os.getcwd()
    unittest.main()