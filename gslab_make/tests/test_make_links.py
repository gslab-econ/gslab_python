#! /usr/bin/env python

import unittest
import sys
import os
import shutil
import re

sys.path.append('../..')
from gslab_make import start_make_logging, make_links, clear_dirs, remove_dir
from gslab_make.tests import nostderrout
    
    
class testMakeLinks(unittest.TestCase):

    def setUp(self):
        self.output_dir = '../output/'

        with nostderrout():
            clear_dirs(self.output_dir)      
            start_make_logging(self.output_dir + 'make.log')  

    def test_legal_input(self):
        default_makelog_file = os.path.join(self.output_dir, 'make.log')
        default_links_dir = '../external_links/'
        self.assertFalse(os.path.isdir(default_links_dir))
        links = './input/links_legal.txt'
        
        with nostderrout():
            make_links(links, quiet = True)
            
        self.assertTrue(os.path.isdir(default_links_dir))       
                
        links_data = open(links, 'rU').readlines()
        comments_ct = self.find_comment_lines(links_data)
        wildcard_lines_ct = len([ l for l in links_data if '*' in l ])
        wildcard_files_ct = len([ f for f in os.listdir('./input/') if f.endswith('_files.txt') ])
        number_of_links = len(links_data) - comments_ct - wildcard_lines_ct + wildcard_files_ct
        success_count = self.get_string_count(default_makelog_file, 'Symlink successfully created.')
        self.assertTrue(success_count == number_of_links)
        
        prefix_files_ct = len([ f for f in os.listdir('../external_links/') if f.startswith('input_') ])
        self.assertEqual(prefix_files_ct, wildcard_files_ct)
        
        f = open('../external_links/ext.txt', 'r')
        self.assertTrue(f.readline().startswith('rev\tdir\tfile\toutdir\toutfile\tnotes'))
        f.close()
        
        logfile_data = open(default_makelog_file, 'rU').read()
        self.assertNotIn('Error', logfile_data)
        
    def test_multiple_input_list(self):
        default_makelog_file = os.path.join(self.output_dir, 'make.log')
        default_links_dir = '../external_links/'
        self.assertFalse(os.path.isdir(default_links_dir))        

        with nostderrout():
            make_links(['./input/link_a.txt', './input/link_b.txt'], quiet = True)

        self.assertTrue(os.path.isdir(default_links_dir))   
        links1_data = open('./input/link_a.txt', 'rU').readlines()
        links2_data = open('./input/link_b.txt', 'rU').readlines()
        comments1 = self.find_comment_lines(links1_data)
        comments2 = self.find_comment_lines(links2_data)
        number_of_links = len(links1_data) + len(links2_data) - comments1 - comments2
        success_count = self.get_string_count(default_makelog_file, 'Symlink successfully created.')
        self.assertEqual(success_count, number_of_links)
        logfile_data = open(default_makelog_file, 'rU').read()
        self.assertNotIn('Error', logfile_data)
        
    def test_multiple_input_string(self):
        default_makelog_file = os.path.join(self.output_dir, 'make.log')
        default_links_dir = '../external_links/'
        self.assertFalse(os.path.isdir(default_links_dir))        

        with nostderrout():
            make_links('./input/link_a.txt ./input/link_b.txt', quiet = True)

        self.assertTrue(os.path.isdir(default_links_dir))   
        links1_data = open('./input/link_a.txt', 'rU').readlines()
        links2_data = open('./input/link_b.txt', 'rU').readlines()
        comments1 = self.find_comment_lines(links1_data)
        comments2 = self.find_comment_lines(links2_data)
        number_of_links = len(links1_data) + len(links2_data) - comments1 - comments2
        success_count = self.get_string_count(default_makelog_file, 'Symlink successfully created.')
        self.assertEqual(success_count, number_of_links)
        logfile_data = open(default_makelog_file, 'rU').read()
        self.assertNotIn('Error', logfile_data)        
        
    def test_wildcard_input(self):
        default_makelog_file = os.path.join(self.output_dir, 'make.log')
        default_links_dir = '../external_links/'
        self.assertFalse(os.path.isdir(default_links_dir))        

        with nostderrout():
            make_links('./input/link_*.txt', quiet = True)

        self.assertTrue(os.path.isdir(default_links_dir))   
        links1_data = open('./input/link_a.txt', 'rU').readlines()
        links2_data = open('./input/link_b.txt', 'rU').readlines()
        comments1 = self.find_comment_lines(links1_data)
        comments2 = self.find_comment_lines(links2_data)
        number_of_links = len(links1_data) + len(links2_data) - comments1 - comments2
        success_count = self.get_string_count(default_makelog_file, 'Symlink successfully created.')
        self.assertEqual(success_count, number_of_links)
        logfile_data = open(default_makelog_file, 'rU').read()
        self.assertNotIn('Error', logfile_data)
    
    def test_illegal_input(self):
        default_makelog_file = self.output_dir + 'make.log'     
        links = './input/links_illegal.txt'
        
        with nostderrout():
            make_links(links, quiet = True)
        
        success_count = self.get_string_count(default_makelog_file, 'Symlink successfully created.')        
        self.assertEqual(success_count, 0)     
    
    def get_string_count(self, logfile, string):
        logfile_data = open(logfile, 'rU').readlines()
        count = 0
        for line in logfile_data:
            if line.startswith(string):
                count += 1

        return count
        
    def find_comment_lines(self, lines):
        comments = 0
        for line in lines:
            if re.match('^#', line):
                comments += 1
            if re.match('^\\n', line):
                comments += 1
        return comments        
   
    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
        if os.path.isdir('../external/'):
            shutil.rmtree('../external/')
        if os.path.isdir('../external_links/'):
            remove_dir('../external_links/')
        if os.path.isdir('../cust_data_links/'):
            remove_dir('../cust_data_links/')
    
    
if __name__ == '__main__':
    # Ensure the script is run from its own directory 
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    unittest.main()
    
