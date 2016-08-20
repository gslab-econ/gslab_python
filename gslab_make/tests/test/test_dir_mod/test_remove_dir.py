#! /usr/bin/env python

import unittest, sys, os, shutil, contextlib
sys.path.append('../..')
from dir_mod import remove_dir, clear_dirs
from get_externals import get_externals
from make_links import make_links
from nostderrout import nostderrout


class testRemoveDir(unittest.TestCase):

    def setUp(self):
        clear_dirs('./externals/')
        get_externals('./input/externals_remove_dir.txt', 
                        external_dir = './externals/', 
                        makelog = '', 
                        quiet = True)
        make_links('./input/links_remove_dir.txt', 
                        makelog = '',
                        quiet = True)
    
    def test_safe_symlinks(self):
        with nostderrout():
            remove_dir('../external_links/')
        test_isfile = os.path.isfile('./input/externals_legal.txt')
        self.assertTrue(test_isfile)
    
    def test_data_links(self):
        self.assertTrue(os.path.exists('../external_links/externals/'))
        file_list_dest = os.listdir('../external_links/externals/')
        file_list_src = os.listdir('./externals/')
        self.assertTrue(file_list_src == file_list_dest)

        self.assertTrue(os.path.exists('../external_links/externals/internal/'))
        subdir_file_list_dest = os.listdir('../external_links/externals/internal/')
        subdir_file_list_src = os.listdir('./externals/internal/')
        self.assertTrue(subdir_file_list_src == subdir_file_list_dest)

        with nostderrout():
            remove_dir('../external_links')

        self.assertFalse(os.path.exists('../external_links/'))
        file_list_src_old = file_list_src
        file_list_src_new = os.listdir('./externals/')
        self.assertTrue(file_list_src_old == file_list_src_new)
    
    def test_standard(self):
        self.assertTrue(os.path.exists('./externals/'))        
        file_list = os.listdir('./externals/')
        self.assertTrue(len(file_list) > 0)
        with nostderrout():
            remove_dir('./externals/')
        self.assertFalse(os.path.exists('./externals/'))
        
    def tearDown(self):
        if os.path.isdir('./externals/'):
            shutil.rmtree('./externals/')
        if os.path.isdir('../external_links/'):
            remove_dir('../external_links/')
        if os.path.isfile('./get_externals.log'):
            os.remove('./get_externals.log')
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
