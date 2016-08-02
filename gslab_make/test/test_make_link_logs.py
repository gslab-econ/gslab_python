#! /usr/bin/env python

import unittest, sys, os, shutil, re
sys.path.append('..')
from py.make_link_logs import make_link_logs
from py.make_links import make_links
from py.dir_mod import remove_dir
from nostderrout import nostderrout
    
    
class testMakeLinkLogs(unittest.TestCase):

    def setUp(self):
        self.test_dir = './input/'
        files = os.listdir(self.test_dir)
        files = [ f for f in files if (os.path.isfile(os.path.join(self.test_dir, f)) 
                                       and not f.startswith('.')) ]
        self.file_count = len(files)
            
    def test_default_log(self):
        default_stats = '../log/link_stats.log'
        default_heads = '../log/link_heads.log'
        default_orig = '../log/link_orig.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))
        self.assertFalse(os.path.exists(default_orig))

        with nostderrout():
            make_link_logs('./input/links_simple.txt')

        self.assertTrue(os.path.exists(default_stats))
        self.assertTrue(os.path.exists(default_heads))
        self.assertTrue(os.path.exists(default_orig))
        stats_count = len(open(default_stats).readlines()) - 1
        self.assertEqual(stats_count, self.file_count)
        heads_count = self.get_string_count(default_heads, '-' * 65) - 1
        self.assertEqual(heads_count, self.file_count)
        links_data = open('./input/links_simple.txt', 'rU').readlines()
        comments = self.find_comment_lines(links_data)
        number_of_links = len(links_data) - comments
        logged_links = len(open(default_orig, 'rU').readlines()) - 1
        self.assertTrue(number_of_links >= logged_links)           
                         
    def test_custom_log(self):
        custom_stats = '../output/custom_link_stats.log'
        custom_heads = '../output/custom_link_heads.log'
        custom_orig = '../output/custom_link_orig.log'
        self.assertFalse(os.path.exists(custom_stats))
        self.assertFalse(os.path.exists(custom_heads))
        self.assertFalse(os.path.exists(custom_orig))
        
        with nostderrout():
            make_link_logs('./input/links_simple.txt',
                            link_logs_dir = '../output/',
                            link_stats_file = 'custom_link_stats.log',
                            link_heads_file = 'custom_link_heads.log',
                            link_orig_file = 'custom_link_orig.log')  
        
        self.assertTrue(os.path.exists(custom_stats))
        self.assertTrue(os.path.exists(custom_heads))
        self.assertTrue(os.path.exists(custom_orig))            
        stats_count = len(open(custom_stats).readlines()) - 1
        self.assertEqual(stats_count, self.file_count)
        heads_count = self.get_string_count(custom_heads, '-' * 65) - 1
        self.assertEqual(heads_count, self.file_count)
        
    def test_multiple_input_list(self):
        default_stats = '../log/link_stats.log'
        default_heads = '../log/link_heads.log'
        default_orig = '../log/link_orig.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))
        self.assertFalse(os.path.exists(default_orig))

        with nostderrout():
            make_link_logs(['./input/link_a.txt', './input/link_b.txt'])

        self.assertTrue(os.path.exists(default_stats))
        self.assertTrue(os.path.exists(default_heads))
        self.assertTrue(os.path.exists(default_orig))    

        links1_data = open('./input/link_a.txt', 'rU').readlines()
        links2_data = open('./input/link_b.txt', 'rU').readlines()
        comments1 = self.find_comment_lines(links1_data)
        comments2 = self.find_comment_lines(links2_data)
        number_of_links = len(links1_data) + len(links2_data) - comments1 - comments2
        logged_links = len(open(default_orig, 'rU').readlines()) - 1
        self.assertEqual(number_of_links, logged_links)        
        
    def test_multiple_input_string(self):
        default_stats = '../log/link_stats.log'
        default_heads = '../log/link_heads.log'
        default_orig = '../log/link_orig.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))
        self.assertFalse(os.path.exists(default_orig))

        with nostderrout():
            make_link_logs('./input/link_a.txt ./input/link_b.txt')

        self.assertTrue(os.path.exists(default_stats))
        self.assertTrue(os.path.exists(default_heads))
        self.assertTrue(os.path.exists(default_orig))    

        links1_data = open('./input/link_a.txt', 'rU').readlines()
        links2_data = open('./input/link_b.txt', 'rU').readlines()
        comments1 = self.find_comment_lines(links1_data)
        comments2 = self.find_comment_lines(links2_data)
        number_of_links = len(links1_data) + len(links2_data) - comments1 - comments2
        logged_links = len(open(default_orig, 'rU').readlines()) - 1
        self.assertEqual(number_of_links, logged_links)           
        
    def test_wildcard_input(self):
        default_stats = '../log/link_stats.log'
        default_heads = '../log/link_heads.log'
        default_orig = '../log/link_orig.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))
        self.assertFalse(os.path.exists(default_orig))

        with nostderrout():
            make_link_logs('./input/link_*.txt')

        self.assertTrue(os.path.exists(default_stats))
        self.assertTrue(os.path.exists(default_heads))
        self.assertTrue(os.path.exists(default_orig))     

        links1_data = open('./input/link_a.txt', 'rU').readlines()
        links2_data = open('./input/link_b.txt', 'rU').readlines()
        comments1 = self.find_comment_lines(links1_data)
        comments2 = self.find_comment_lines(links2_data)
        number_of_links = len(links1_data) + len(links2_data) - comments1 - comments2
        logged_links = len(open(default_orig, 'rU').readlines()) - 1
        self.assertEqual(number_of_links, logged_links)
        
    def test_lower_recur_lim(self):
        default_stats = '../log/link_stats.log'
        default_heads = '../log/link_heads.log'
        default_orig = '../log/link_orig.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))
        self.assertFalse(os.path.exists(default_orig))
        
        with nostderrout():
            make_link_logs('./input/links_simple.txt',
                            recur_lim = 1)  
        
        self.assertTrue(os.path.exists(default_stats))
        self.assertTrue(os.path.exists(default_heads))
        self.assertTrue(os.path.exists(default_orig))
        stats_count = len(open(default_stats).readlines()) - 1
        self.assertEqual(stats_count, 0)
        heads_count = self.get_string_count(default_heads, '-' * 65) - 1
        self.assertEqual(heads_count, 0)        
        
    def test_no_recur_lim (self):
        default_stats = '../log/link_stats.log'
        default_heads = '../log/link_heads.log'
        default_orig = '../log/link_orig.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))
        self.assertFalse(os.path.exists(default_orig))
        
        with nostderrout():
            make_link_logs('./input/links_simple.txt',
                            recur_lim = False)

        self.assertTrue(os.path.exists(default_stats))
        self.assertTrue(os.path.exists(default_heads))
        self.assertTrue(os.path.exists(default_orig))
        
        file_count = 0
        for root, dirs, files in os.walk(self.test_dir):
            root = os.path.abspath(root)
            this_dir = os.path.basename(root)
            if not this_dir.startswith('.'):
                files = [ f for f in files if not f.startswith('.') ]
                file_count += len(files)
            else:
                del dirs[:]        
        
        stats_count = len(open(default_stats).readlines()) - 1
        self.assertEqual(stats_count, file_count)
        heads_count = self.get_string_count(default_heads, '-' * 65) - 1
        self.assertEqual(heads_count, file_count)
        orig_count = len(open(default_orig).readlines()) - 1
        links_count = len(open('./input/links_simple.txt').readlines())
        self.assertEqual(orig_count, links_count)    
        
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
        if os.path.exists('../log/link_stats.log'):
            os.remove('../log/link_stats.log')  
        if os.path.exists('../log/link_heads.log'):
            os.remove('../log/link_heads.log')    
        if os.path.exists('../log/link_orig.log'):
            os.remove('../log/link_orig.log')              
        if os.path.isdir('../external_links/'):
            remove_dir('../external_links/')
        if os.path.exists('./make_links.log'):
            os.remove('./make_links.log')
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
