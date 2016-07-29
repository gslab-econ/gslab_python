#! /usr/bin/env python

import unittest, os, sys
sys.path.append('..')
from py.getngrams import *
    
class testNgramDownload(unittest.TestCase):

    def test_download(self):
        downloadGoogleNgrams("political media consultants", saveFolder = "./", filename = "consultants_media")
        self.assertTrue(os.path.isfile('consultants_media.csv'))
        os.remove('consultants_media.csv')
   
if __name__ == '__main__':
    os.getcwd()
    unittest.main()